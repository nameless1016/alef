"""Plain dataclasses for the workspace. No Streamlit, no I/O."""
import time
import uuid
from dataclasses import dataclass, field
from typing import List, Optional

PRIORITIES = ("high", "medium", "low")
COLUMNS = (
    ("current", "Current"),
    ("progress", "In progress"),
    ("backlog", "Backlog"),
    ("blocked", "Blocked"),
    ("done", "Done"),
)
COLUMN_LABELS = dict(COLUMNS)
ACCENTS = {
    "Coral": ("#d1565f", "#c25560"),
    "Amber": ("#d8a85a", "#c99a4e"),
    "Teal": ("#4fb3bf", "#45a1ac"),
    "Violet": ("#a07cd6", "#9068c8"),
    "Lime": ("#b9c23c", "#a8b132"),
}
ENGINES = ["Godot 4.3", "Godot 4.2", "Unity 6", "Unreal 5.4"]


def new_id() -> str:
    return uuid.uuid4().hex[:6]


@dataclass
class Project:
    name: str = "Untitled project"
    tagline: str = ""
    description: str = ""
    goal: str = ""
    engine: str = "Godot 4.3"
    user_name: str = "there"
    branch: str = "main"
    target: str = ""                 # ISO date
    milestone_title: str = ""
    milestone_date: str = ""         # ISO date
    scope_load: int = 50
    budget_used: int = 50
    baseline: int = 0                # % done before tasks were tracked
    accent: str = "Coral"
    include_docs: bool = True
    include_maps: bool = True
    status: str = "Project active"
    version: str = "Alef 0.8"
    format: str = "Markdown"


@dataclass
class Task:
    title: str
    column: str = "current"
    priority: str = "medium"
    estimate: str = "30m"
    due: Optional[str] = None        # ISO date or None
    tags: List[str] = field(default_factory=list)
    description: str = ""
    id: str = field(default_factory=new_id)
    created_at: float = field(default_factory=time.time)

    @property
    def done(self) -> bool:
        return self.column == "done"


@dataclass
class Message:
    role: str                        # "user" | "alef"
    text: str
    ts: float = field(default_factory=time.time)


@dataclass
class Chat:
    title: str
    subtitle: str = "Planning"
    messages: List[Message] = field(default_factory=list)
    id: str = field(default_factory=new_id)


@dataclass
class Document:
    title: str
    kind: str = "doc"                # "doc" | "map"
    subtitle: str = ""
    markdown: str = ""
    id: str = field(default_factory=new_id)

    @property
    def page(self) -> str:
        return f"{self.kind}:{self.id}"

    @property
    def filename(self) -> str:
        slug = "".join(c.lower() if c.isalnum() else "-" for c in self.title).strip("-")
        return f"{slug or 'untitled'}.md"


@dataclass
class Change:
    kind: str
    title: str
    text: str
    ts: float = field(default_factory=time.time)
    synced: bool = False
    id: str = field(default_factory=new_id)
