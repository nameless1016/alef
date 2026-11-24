"""Sandboxed system prompt and scoped chat message builder for Alef."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from services.models import Task
from services.workspace import Workspace

from .prompt_template import SYSTEM_PROMPT_TEMPLATE

_STATE_TAG_RE = re.compile(r"<\s*(/?)\s*project_state\s*>", re.IGNORECASE)
_LONG_DOC_TAG_RE = re.compile(r"<\s*(/?)\s*long_document\s*>", re.IGNORECASE)

SYNC_USER_PROMPT = (
    "I updated the project workspace (see change log in project state). "
    "Acknowledge the changes briefly, assess any impact on scope or deadline, "
    "and state the next immediate step."
)


@dataclass(frozen=True)
class ProjectStatePayload:
    active_project: str
    short_doc: str
    map: str
    tasks: str
    project_deadline: str
    current_tasks: str
    change_log: str


def sanitize_state_value(text: str) -> str:
    """Neutralize any attempt to close or inject <project_state> tags."""
    if not text:
        return ""
    return _STATE_TAG_RE.sub(lambda m: f"[{m.group(1)}project_state]", text)


def _sanitize_long_doc(text: str) -> str:
    cleaned = sanitize_state_value(text or "")
    return _LONG_DOC_TAG_RE.sub(lambda m: f"[{m.group(1)}long_document]", cleaned)


def format_task_line(task: Task) -> str:
    if task.column == "done":
        box = "[x]"
    elif task.column == "progress":
        box = "[/]"
    else:
        box = "[ ]"

    tags = [t.strip().lstrip("#").lower() for t in (task.tags or []) if t and t.strip()]
    if task.column == "blocked" and "blocked" not in tags:
        tags.append("blocked")
    elif task.column == "backlog" and "backlog" not in tags:
        tags.append("backlog")

    parts = [f"- {box} {task.title.strip()}"]
    if tags:
        parts.append(" ".join(f"#{t}" for t in tags))
    if task.due:
        parts.append(f"(due: {task.due})")
    return " ".join(parts)


def build_project_state(ws: Workspace) -> ProjectStatePayload:
    p = ws.project
    initialized = ws.is_initialized()

    active_parts = [p.name.strip() or "Untitled project"]
    if p.engine:
        active_parts.append(f"Engine: {p.engine}")
    if p.tagline:
        active_parts.append(p.tagline)
    active_project = " | ".join(active_parts)

    if not initialized:
        short_doc = "(empty - project not initialized)"
        map_text = "(empty)"
    else:
        if not p.include_docs:
            short_doc = "(excluded by settings)"
        else:
            sd = ws.short_doc()
            short_doc = sd.markdown.strip() if sd and sd.markdown.strip() else "(empty)"

        if not p.include_maps:
            map_text = "(excluded by settings)"
        else:
            pm = ws.primary_map()
            map_text = pm.markdown.strip() if pm and pm.markdown.strip() else "(empty)"

    tasks_text = "\n".join(format_task_line(t) for t in ws.tasks) if ws.tasks else "(none)"
    curr = ws.current_tasks()
    current_tasks_text = "\n".join(format_task_line(t) for t in curr) if curr else "(none)"

    deadline_parts = []
    if p.target:
        deadline_parts.append(f"Target: {p.target}")
    if p.milestone_date:
        m_label = f" ({p.milestone_title})" if p.milestone_title else ""
        deadline_parts.append(f"Next milestone: {p.milestone_date}{m_label}")
    deadline_text = " | ".join(deadline_parts) if deadline_parts else "(not set)"

    change_log = ws.change_log_text() or "(none)"

    return ProjectStatePayload(
        active_project=sanitize_state_value(active_project),
        short_doc=sanitize_state_value(short_doc),
        map=sanitize_state_value(map_text),
        tasks=sanitize_state_value(tasks_text),
        project_deadline=sanitize_state_value(deadline_text),
        current_tasks=sanitize_state_value(current_tasks_text),
        change_log=sanitize_state_value(change_log),
    )


_PROSE_FIELD_LABELS = {
    "{{active_project}}": "Active Project",
    "{{short_doc}}": "Short Project Summary",
    "{{map}}": "Project Map",
    "{{tasks}}": "Tasks",
    "{{project_deadline}}": "Project Deadline",
    "{{current_tasks}}": "Current Task(s)",
    "{{change_log}}": "Changes Since Last Turn",
}


def build_system_prompt(ws: Workspace) -> str:
    state = build_project_state(ws)
    state_replacements = {
        "{{active_project}}": state.active_project,
        "{{short_doc}}": state.short_doc,
        "{{map}}": state.map,
        "{{tasks}}": state.tasks,
        "{{project_deadline}}": state.project_deadline,
        "{{current_tasks}}": state.current_tasks,
        "{{change_log}}": state.change_log,
    }
    start = SYSTEM_PROMPT_TEMPLATE.index("<project_state>")
    end = SYSTEM_PROMPT_TEMPLATE.index("</project_state>") + len("</project_state>")
    before = SYSTEM_PROMPT_TEMPLATE[:start]
    sandbox = SYSTEM_PROMPT_TEMPLATE[start:end]
    after = SYSTEM_PROMPT_TEMPLATE[end:]

    for placeholder, value in state_replacements.items():
        sandbox = sandbox.replace(placeholder, value)
    for placeholder, label in _PROSE_FIELD_LABELS.items():
        before = before.replace(placeholder, label)
        after = after.replace(placeholder, label)
    return before + sandbox + after


def _scoped_history(ws: Workspace, chat_id: Optional[str], history_limit: int) -> List[dict]:
    if not chat_id:
        return []
    chat = ws.get_chat(chat_id)
    if not chat or not chat.messages:
        return []
    window = chat.messages[-history_limit:] if history_limit > 0 else chat.messages
    result: List[dict] = []
    for m in window:
        role = "user" if m.role == "user" else "assistant"
        result.append({"role": role, "content": m.text})
    return result


def build_chat_messages(ws: Workspace, chat_id: str, history_limit: int = 12) -> List[dict]:
    """Build [system, ...scoped chat history] without duplicating the last user message."""
    messages = [{"role": "system", "content": build_system_prompt(ws)}]
    messages.extend(_scoped_history(ws, chat_id, history_limit))
    return messages


def build_sync_messages(ws: Workspace, chat_id: Optional[str], history_limit: int = 12) -> List[dict]:
    """Build messages for the explicit Change-Sync Gate ('Update Alef') action."""
    messages = [{"role": "system", "content": build_system_prompt(ws)}]
    messages.extend(_scoped_history(ws, chat_id, history_limit))
    messages.append({"role": "user", "content": SYNC_USER_PROMPT})
    return messages


def build_recontextualize_messages(ws: Workspace, doc_id: str, max_chars: int = 16000) -> List[dict]:
    """Build [system, user] messages carrying a read-only Long Document for Short Doc refresh."""
    doc = ws.get_document(doc_id)
    title = sanitize_state_value(doc.title) if doc else "Long Document"
    body = _sanitize_long_doc(doc.markdown if doc else "")
    trunc_note = ""
    if len(body) > max_chars:
        body = body[:max_chars].rstrip()
        trunc_note = f"\n\n[Note: Long document was truncated to {max_chars} characters for context limits.]"

    user_prompt = (
        f"Recontextualize the Short Project Summary from my Long Document titled \"{title}\". "
        "Preserve Genre/Concept, Core Loop, Engine/Platform, Key Technical Architecture, "
        "Target Deadline, and Current Milestone goal in strictly under 300 words. "
        "Do NOT attempt to edit the Long Document; emit the refreshed summary inside <doc_update> "
        "at the end of your reply.\n\n"
        f"<long_document>\n{body}{trunc_note}\n</long_document>"
    )
    return [
        {"role": "system", "content": build_system_prompt(ws)},
        {"role": "user", "content": user_prompt},
    ]
