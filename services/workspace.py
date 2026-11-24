"""The Workspace: single source of truth for everything the UI shows.

Pure Python. Every mutation goes through a method here, which also logs a
change entry and notifies subscribers (used for autosave). When the AI
arrives it talks to this same object through `context_snapshot()` and
`apply_action()`, so UI and AI can never drift apart.
"""
import time
from dataclasses import asdict, fields
from datetime import date
from typing import Callable, Dict, List, Optional

from .formatting import number_word, parse_estimate
from .models import (COLUMN_LABELS, PRIORITIES, Change, Chat, Document, Message,
                     Project, Task)

PRIORITY_RANK = {p: i for i, p in enumerate(PRIORITIES)}


class Workspace:
    def __init__(self, project: Project, tasks=None, chats=None, documents=None,
                 changes=None, note: str = "", last_sync: Optional[float] = None):
        self.project = project
        self.tasks: List[Task] = tasks or []
        self.chats: List[Chat] = chats or []
        self.documents: List[Document] = documents or []
        self.changes: List[Change] = changes or []
        self.note = note
        self.last_sync = last_sync if last_sync is not None else time.time()
        self._listeners: List[Callable] = []

    # ------------------------------------------------------------ plumbing
    def subscribe(self, fn: Callable) -> None:
        self._listeners.append(fn)

    def _touch(self) -> None:
        for fn in self._listeners:
            fn(self)

    def log_change(self, kind: str, title: str, text: str) -> None:
        """Record an unsynced change; repeated edits of one thing coalesce."""
        for c in self.changes:
            if not c.synced and c.kind == kind:
                c.title, c.text, c.ts = title, text, time.time()
                return
        self.changes.insert(0, Change(kind=kind, title=title, text=text))

    # --------------------------------------------------------------- tasks
    def get_task(self, task_id: str) -> Optional[Task]:
        return next((t for t in self.tasks if t.id == task_id), None)

    def tasks_in(self, column: str) -> List[Task]:
        return [t for t in self.tasks if t.column == column]

    def open_tasks(self) -> List[Task]:
        return [t for t in self.tasks if not t.done]

    def find_task(self, query: str) -> Optional[Task]:
        q = query.strip().lower().rstrip(".")
        if not q:
            return None
        pool = self.open_tasks()
        return (next((t for t in pool if t.title.lower() == q), None)
                or next((t for t in pool if q in t.title.lower()), None))

    def add_task(self, title: str, column: str = "current", priority: str = "medium",
                 estimate: str = "30m", due: Optional[str] = None, tags=None,
                 description: str = "") -> Task:
        task = Task(title=title.strip(), column=column if column in COLUMN_LABELS else "current",
                    priority=priority if priority in PRIORITIES else "medium",
                    estimate=estimate, due=due, tags=list(tags or []), description=description)
        self.tasks.append(task)
        self._tasks_changed()
        return task

    def update_task(self, task_id: str, **fields_) -> Optional[Task]:
        task = self.get_task(task_id)
        if not task:
            return None
        for key, value in fields_.items():
            if hasattr(task, key) and key not in ("id", "created_at"):
                setattr(task, key, value)
        self._tasks_changed()
        return task

    def set_done(self, task_id: str, done: bool) -> None:
        self.update_task(task_id, column="done" if done else "current")

    def toggle_done(self, task_id: str) -> None:
        task = self.get_task(task_id)
        if task:
            self.set_done(task_id, not task.done)

    def delete_task(self, task_id: str) -> None:
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self._tasks_changed()

    def _tasks_changed(self) -> None:
        self.log_change("tasks", "Tasks changed",
                        "Current priorities or completion state moved since the last context sync.")
        self._touch()

    # --------------------------------------------------------------- chats
    def get_chat(self, chat_id: str) -> Optional[Chat]:
        return next((c for c in self.chats if c.id == chat_id), None)

    def new_chat(self, title: str = "") -> Chat:
        title = title.strip() or f"New chat {len(self.chats) + 1}"
        chat = Chat(title=title, subtitle=f"Planning · {self.project.name}")
        self.chats.append(chat)
        self._touch()
        return chat

    def rename_chat(self, chat_id: str, title: str) -> None:
        chat = self.get_chat(chat_id)
        if chat and title.strip():
            chat.title = title.strip()
            self._touch()

    def delete_chat(self, chat_id: str) -> None:
        self.chats = [c for c in self.chats if c.id != chat_id]
        self._touch()

    def add_message(self, chat_id: str, role: str, text: str) -> Optional[Message]:
        chat = self.get_chat(chat_id)
        if not chat:
            return None
        msg = Message(role=role, text=text)
        chat.messages.append(msg)
        self._touch()
        return msg

    # ----------------------------------------------------------- documents
    def get_document(self, doc_id: str) -> Optional[Document]:
        return next((d for d in self.documents if d.id == doc_id), None)

    def docs(self, kind: str) -> List[Document]:
        return [d for d in self.documents if d.kind == kind]

    def new_document(self, kind: str, title: str) -> Document:
        title = title.strip() or ("Untitled map" if kind == "map" else "Untitled document")
        if kind == "map":
            body = f"# {title}\n## Branch\n### Leaf"
            sub = "Explore the structure directly from its Markdown hierarchy."
        else:
            body = f"# {title}\n\nStart writing here."
            sub = "Editable design source of truth."
        doc = Document(title=title, kind=kind, subtitle=sub, markdown=body)
        self.documents.append(doc)
        self.log_change(doc.page, f"{doc.title} created", "New file added to Alef's working context.")
        self._touch()
        return doc

    def update_document(self, doc_id: str, markdown: Optional[str] = None,
                        title: Optional[str] = None) -> None:
        doc = self.get_document(doc_id)
        if not doc:
            return
        changed = False
        if markdown is not None and markdown != doc.markdown:
            doc.markdown, changed = markdown, True
        if title is not None and title.strip() and title.strip() != doc.title:
            doc.title, changed = title.strip(), True
        if changed:
            self.log_change(doc.page, f"{doc.title} updated",
                            "Content changed since the last context sync.")
            self._touch()

    def delete_document(self, doc_id: str) -> None:
        self.documents = [d for d in self.documents if d.id != doc_id]
        self._touch()

    # ------------------------------------------------------------- changes
    def changes_view(self) -> List[Change]:
        return sorted(self.changes, key=lambda c: c.ts, reverse=True)

    def unsynced_count(self) -> int:
        return sum(1 for c in self.changes if not c.synced)

    def sync_context(self) -> dict:
        for c in self.changes:
            c.synced = True
        self.last_sync = time.time()
        self._touch()
        return self.context_snapshot()

    # ------------------------------------------------------------- derived
    def _hours(self, task: Task) -> float:
        return parse_estimate(task.estimate) or 0.0

    def progress(self) -> int:
        tracked = [t for t in self.tasks if t.column != "blocked"]
        total = sum(self._hours(t) for t in tracked)
        b = self.project.baseline
        if total <= 0:
            return b
        earned = sum(self._hours(t) for t in tracked if t.column == "done")
        earned += 0.5 * sum(self._hours(t) for t in tracked if t.column == "progress")
        return round(b + (100 - b) * earned / total)

    def critical_count(self) -> int:
        return sum(1 for t in self.open_tasks() if t.priority == "high")

    def milestone(self, today: Optional[date] = None) -> dict:
        today = today or date.today()
        p = self.project
        d = date.fromisoformat(p.milestone_date) if p.milestone_date else None
        return {
            "title": p.milestone_title or "No milestone set",
            "date": d,
            "days_left": max(0, (d - today).days) if d else None,
            "critical": self.critical_count(),
        }

    def scope_health(self) -> dict:
        blocked = self.tasks_in("blocked")
        load = self.project.scope_load
        if load >= 85:
            return {"label": "At risk", "tone": "risk",
                    "text": "Scope load is past what the slice can carry. Cut before adding anything."}
        if blocked:
            n = len(blocked)
            noun = "item is" if n == 1 else "items are"
            keep = "it" if n == 1 else "them"
            return {"label": "Needs attention", "tone": "warn",
                    "text": f"{number_word(n)} blocked {noun} deliberately parked. "
                            f"Keep {keep} there until the slice gate passes."}
        if load >= 60:
            return {"label": "Needs attention", "tone": "warn",
                    "text": "Scope load is climbing. Check what is outside the slice."}
        return {"label": "On track", "tone": "ok", "text": "Nothing is blocked and scope load is healthy."}

    def scope_watch(self) -> str:
        blocked = self.tasks_in("blocked")
        if blocked:
            return f"Watch “{blocked[0].title}”. It is outside the current slice."
        return "Scope load is climbing." if self.project.scope_load >= 60 else "Scope is under control."

    def focus_tasks(self, n: int = 2) -> List[Task]:
        pool = [t for t in self.tasks if t.column in ("current", "progress")]
        pool.sort(key=lambda t: (PRIORITY_RANK.get(t.priority, 9), t.due or "9999-12-31", t.created_at))
        return pool[:n]

    def context_snapshot(self) -> dict:
        """Everything an AI needs to answer; mirrors the 'Loaded context' bar."""
        p = self.project
        snap = {
            "project": {"name": p.name, "engine": p.engine, "description": p.description,
                        "progress": self.progress(), "scope_load": p.scope_load},
            "tasks": [asdict(t) for t in self.tasks],
            "documents": [], "maps": [],
            "generated_at": time.time(),
        }
        if p.include_docs:
            snap["documents"] = [{"title": d.title, "markdown": d.markdown} for d in self.docs("doc")]
        if p.include_maps:
            snap["maps"] = [{"title": d.title, "markdown": d.markdown} for d in self.docs("map")]
        return snap

    def context_counts(self) -> Dict[str, int]:
        snap_docs = len(self.docs("doc")) if self.project.include_docs else 0
        snap_maps = len(self.docs("map")) if self.project.include_maps else 0
        return {"documents": snap_docs, "maps": snap_maps, "tasks": len(self.tasks)}

    # ------------------------------------------------------------- actions
    def apply_action(self, action: dict) -> Optional[str]:
        """Execute a structured action (from commands now, from an AI later)."""
        kind = action.get("type")
        if kind == "add_task":
            t = self.add_task(action["title"], column=action.get("column", "current"),
                              priority=action.get("priority", "medium"),
                              estimate=action.get("estimate", "30m"),
                              tags=action.get("tags", ["from-chat"]),
                              description=action.get("description", "Created directly from the Alef conversation."))
            return t.id
        if kind == "complete_task" and self.get_task(action["task_id"]):
            self.set_done(action["task_id"], True)
            return action["task_id"]
        if kind == "move_task" and self.get_task(action["task_id"]):
            self.update_task(action["task_id"], column=action["column"])
            return action["task_id"]
        if kind == "set_note":
            self.note = action["text"]
            self._touch()
            return "note"
        return None

    # --------------------------------------------------------- persistence
    def to_dict(self) -> dict:
        return {
            "project": asdict(self.project),
            "tasks": [asdict(t) for t in self.tasks],
            "chats": [asdict(c) for c in self.chats],
            "documents": [asdict(d) for d in self.documents],
            "changes": [asdict(c) for c in self.changes],
            "note": self.note,
            "last_sync": self.last_sync,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Workspace":
        def build(klass, raw):
            names = {f.name for f in fields(klass)}
            return klass(**{k: v for k, v in raw.items() if k in names})

        chats = []
        for raw in data.get("chats", []):
            raw = dict(raw)
            raw["messages"] = [build(Message, m) for m in raw.get("messages", [])]
            chats.append(build(Chat, raw))
        return cls(
            project=build(Project, data.get("project", {})),
            tasks=[build(Task, t) for t in data.get("tasks", [])],
            chats=chats,
            documents=[build(Document, d) for d in data.get("documents", [])],
            changes=[build(Change, c) for c in data.get("changes", [])],
            note=data.get("note", ""),
            last_sync=data.get("last_sync"),
        )
