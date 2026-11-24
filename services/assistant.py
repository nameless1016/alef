"""Assistant interface. The AI plugs in here.

`LocalAssistant` is a deterministic command router so every chat feature
works without a model key. `AlefAssistant` connects to the configured OpenAI-
compatible LLM (`gpt-6-luna`), builds sandboxed `<project_state>` prompts,
and parses the 4 allowed trailing XML tags into `Workspace.apply_action()` calls.
"""
import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional, Protocol

from .ai.llm_client import LLMClient, OpenAILLMClient, load_config
from .ai.prompt_builder import (
    build_chat_messages,
    build_recontextualize_messages,
    build_sync_messages,
)
from .ai.tag_parser import parse_response, to_actions
from .formatting import parse_estimate
from .models import COLUMN_LABELS
from .workspace import PRIORITY_RANK, Workspace

logger = logging.getLogger(__name__)

_TRUNCATION_NOTICE = (
    "Note: My reply hit the 500-token limit before finishing the structured update, "
    "so no files were changed. Ask me to keep the update brief to retry."
)


@dataclass
class AssistantReply:
    text: str
    actions: List[dict] = field(default_factory=list)   # executed via Workspace.apply_action
    synced_changes: bool = False
    warnings: List[str] = field(default_factory=list)
    is_error: bool = False


class Assistant(Protocol):
    def reply(self, ws: Workspace, chat_id: str, user_text: str) -> AssistantReply: ...


_ADD = re.compile(r"^\s*add\s+(?:a\s+)?task\s*[:\-]\s*(.+)$", re.I | re.S)
_ADD_BARE = re.compile(r"^\s*add\s+(?:a\s+)?task\s*\??\s*$", re.I)
_DONE = re.compile(r"^\s*(?:complete|finish|done)\s*(?:task)?\s*[:\-]?\s*(.+)$", re.I | re.S)


class LocalAssistant:
    def reply(self, ws: Workspace, chat_id: str, user_text: str) -> AssistantReply:
        text = user_text.strip()
        low = text.lower()

        m = _ADD.match(text)
        if m:
            title = m.group(1).strip().rstrip(".")
            return AssistantReply(
                "Added directly to Current. I kept it small enough to finish before the slice review.",
                [{"type": "add_task", "title": title, "column": "current", "estimate": "30m"}])
        if _ADD_BARE.match(text):
            return AssistantReply("What should the task be called? Reply with “Add task: <title>”.")

        m = _DONE.match(text)
        if m:
            task = ws.find_task(m.group(1))
            if task:
                return AssistantReply(f"Marked “{task.title}” complete.",
                                      [{"type": "complete_task", "task_id": task.id}])
            return AssistantReply("I couldn't find an open task matching that. Check the task board for the exact title.")

        if "cut" in low:
            return AssistantReply(self._what_to_cut(ws))
        if "biggest unknown" in low or "unknown" in low:
            return AssistantReply(self._biggest_unknown(ws))
        if any(k in low for k in ("status", "summary", "where are we")):
            return AssistantReply(self._status(ws))

        return AssistantReply(
            "The full assistant isn't connected yet. For now I can add tasks (“Add task: …”), "
            "complete them (“Complete: …”), and answer “What should I cut?”, "
            "“Find the biggest unknown” and “Status”.")

    # ---- canned analyses built from real workspace data -----------------
    def _what_to_cut(self, ws: Workspace) -> str:
        parked = ws.tasks_in("blocked")
        if parked:
            names = ", ".join(f"“{t.title}”" for t in parked)
            return (f"Nothing in the slice needs to go. Keep {names} parked until the gate passes; "
                    "everything in Current and In progress supports the surveillance loop.")
        low = sorted((t for t in ws.open_tasks()),
                     key=lambda t: -PRIORITY_RANK.get(t.priority, 0))
        if low:
            return (f"Nothing is parked. The lowest-priority open task is “{low[0].title}”; "
                    "that is the first thing I would cut.")
        return "Nothing is open, so there is nothing to cut."

    def _biggest_unknown(self, ws: Workspace) -> str:
        pool = [t for t in ws.open_tasks() if t.column != "blocked"]
        if not pool:
            return "No open work left, so the biggest unknown is what comes after the slice."
        research = [t for t in pool if "research" in t.tags]
        pick = research[0] if research else max(pool, key=lambda t: parse_estimate(t.estimate) or 0)
        where = COLUMN_LABELS.get(pick.column, pick.column)
        return (f"“{pick.title}” ({pick.estimate}) is the biggest unknown and it still sits in {where}. "
                "Learn from it before you build more on top.")

    def _status(self, ws: Workspace) -> str:
        done = len(ws.tasks_in("done"))
        return (f"Slice progress is {ws.progress()}%. {done} of {len(ws.tasks)} tasks are done, "
                f"{ws.critical_count()} open tasks are high priority, "
                f"{len(ws.tasks_in('blocked'))} blocked.")


class AlefAssistant:
    """Live LLM-backed Game Dev Producer assistant."""

    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def _invoke(
        self,
        messages: List[dict],
        *,
        sync_on_success: bool,
        allowed_action_types: Optional[set] = None,
    ) -> AssistantReply:
        try:
            completion = self.client.complete(messages)
        except Exception:
            logger.exception("Alef LLM request failed")
            return AssistantReply(
                text=(
                    "I couldn't reach the AI service right now. Your project state and any "
                    "unsynced changes are intact—try again in a moment."
                ),
                actions=[],
                synced_changes=False,
                is_error=True,
            )

        parsed = parse_response(completion.content, completion.finish_reason)
        actions = [] if parsed.truncated else to_actions(parsed)
        if allowed_action_types is not None:
            actions = [a for a in actions if a.get("type") in allowed_action_types]

        reply_text = parsed.reply_text
        if parsed.truncated:
            reply_text = f"{reply_text}\n\n{_TRUNCATION_NOTICE}".strip() if reply_text else _TRUNCATION_NOTICE
        elif not reply_text:
            reply_text = "Updated project state." if actions else "I didn't receive a response. Try again."

        return AssistantReply(
            text=reply_text,
            actions=actions,
            synced_changes=sync_on_success,
            warnings=list(parsed.warnings),
            is_error=False,
        )

    def reply(self, ws: Workspace, chat_id: str, user_text: str) -> AssistantReply:
        messages = build_chat_messages(ws, chat_id)
        cleaned = (user_text or "").strip()
        if cleaned:
            last = messages[-1] if len(messages) > 1 else None
            if not last or last.get("role") != "user" or last.get("content", "").strip() != cleaned:
                messages.append({"role": "user", "content": cleaned})
        return self._invoke(messages, sync_on_success=ws.unsynced_count() > 0)

    def sync_changes(self, ws: Workspace, chat_id: Optional[str]) -> AssistantReply:
        messages = build_sync_messages(ws, chat_id)
        return self._invoke(messages, sync_on_success=True)

    def recontextualize(self, ws: Workspace, doc_id: str, chat_id: Optional[str] = None) -> AssistantReply:
        doc = ws.get_document(doc_id)
        if not doc or not doc.markdown.strip():
            return AssistantReply(
                text="That document is empty—add content before recontextualizing.",
                actions=[],
                synced_changes=False,
                is_error=True,
            )
        messages = build_recontextualize_messages(ws, doc_id)
        return self._invoke(
            messages,
            sync_on_success=False,
            allowed_action_types={"update_short_doc"},
        )


def is_live_ai(assistant: Assistant) -> bool:
    return isinstance(assistant, AlefAssistant)


def get_assistant() -> Assistant:
    """Return live AlefAssistant when ALEF_API_KEY is configured, else LocalAssistant."""
    config = load_config()
    if config is not None:
        return AlefAssistant(OpenAILLMClient(config))
    return LocalAssistant()
