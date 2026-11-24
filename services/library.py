"""A Library holds several projects (each one a Workspace). Pure Python."""
import time
from typing import Callable, Dict, List, Optional, Tuple

from .models import Chat, Project, new_id
from .workspace import Workspace


class Library:
    def __init__(self, workspaces: Dict[str, Workspace], order: List[str], active: str):
        self.workspaces = workspaces
        self.order = order
        self.active_id = active if active in workspaces else order[0]
        # persistence hooks, set by the storage layer
        self.on_workspace_change: Optional[Callable[[str, Workspace], None]] = None
        self.on_index_change: Optional[Callable[["Library"], None]] = None
        for pid, ws in self.workspaces.items():
            self._wire(pid, ws)

    @classmethod
    def single(cls, ws: Workspace, pid: str = "main") -> "Library":
        return cls({pid: ws}, [pid], pid)

    # ------------------------------------------------------------ queries
    @property
    def active(self) -> Workspace:
        return self.workspaces[self.active_id]

    def projects(self) -> List[Tuple[str, Project]]:
        return [(pid, self.workspaces[pid].project) for pid in self.order]

    # ----------------------------------------------------------- mutation
    def _wire(self, pid: str, ws: Workspace) -> None:
        ws.subscribe(lambda w, _pid=pid: self.on_workspace_change and self.on_workspace_change(_pid, w))

    def _index_changed(self) -> None:
        if self.on_index_change:
            self.on_index_change(self)

    def switch(self, pid: str) -> bool:
        if pid not in self.workspaces:
            return False
        self.active_id = pid
        self._index_changed()
        return True

    def create(self, name: str, tagline: str = "", engine: str = "Godot 4.3",
               user_name: str = "there") -> str:
        pid = new_id()
        clean_name = name.strip() or "Untitled project"
        ws = Workspace(Project(name=clean_name, tagline=tagline.strip(),
                               engine=engine, user_name=user_name, branch="main",
                               scope_load=0, budget_used=0, baseline=0, initialized=False),
                       chats=[Chat("Project setup", f"Setup · {clean_name}")],
                       last_sync=time.time())
        self.workspaces[pid] = ws
        self.order.append(pid)
        self._wire(pid, ws)
        self.active_id = pid
        if self.on_workspace_change:
            self.on_workspace_change(pid, ws)
        self._index_changed()
        return pid

    def replace_active(self, ws: Workspace) -> None:
        """Swap the active project's contents (used by clear / load demo)."""
        self.workspaces[self.active_id] = ws
        self._wire(self.active_id, ws)
        if self.on_workspace_change:
            self.on_workspace_change(self.active_id, ws)

    def delete(self, pid: str) -> bool:
        if len(self.order) <= 1 or pid not in self.workspaces:
            return False
        self.workspaces.pop(pid)
        self.order.remove(pid)
        if self.active_id == pid:
            self.active_id = self.order[0]
        self._index_changed()
        return True
