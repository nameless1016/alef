"""Assistant interface. The AI plugs in here.

`LocalAssistant` is a deterministic command router so every chat feature
works today without a model. To add the real AI, implement `Assistant.reply`
(call your model with `ws.context_snapshot()`, return text plus structured
actions) and return it from `get_assistant()`. Nothing in the UI changes.
"""
import re
from dataclasses import dataclass, field
from typing import List, Protocol

from .formatting import parse_estimate
from .models import COLUMN_LABELS
from .workspace import PRIORITY_RANK, Workspace


@dataclass
class AssistantReply:
    text: str
    actions: List[dict] = field(default_factory=list)   # executed via Workspace.apply_action


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


def get_assistant() -> Assistant:
    """Swap this for the real AI-backed assistant later."""
    return LocalAssistant()
