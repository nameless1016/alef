"""JSON persistence for the workspace. Pure Python."""
import json
from pathlib import Path
from typing import Optional

from .workspace import SCHEMA, Workspace

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "workspace.json"


def save(ws: Workspace, path: Path = DATA_PATH) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(ws.to_dict(), indent=2), encoding="utf-8")
        tmp.replace(path)
    except OSError:
        pass  # read-only hosts: the app still works for the session


def load(path: Path = DATA_PATH) -> Optional[Workspace]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema") != SCHEMA:
            return None          # older save (e.g. demo data): start from a clean slate
        return Workspace.from_dict(data)
    except (OSError, ValueError, KeyError, TypeError):
        return None


def reset(path: Path = DATA_PATH) -> None:
    try:
        path.unlink()
    except OSError:
        pass


# ------------------------------------------------------------------ library
from .library import Library  # noqa: E402

DATA_DIR = DATA_PATH.parent
PROJECTS_DIR = DATA_DIR / "projects"
INDEX_PATH = DATA_DIR / "library.json"


def save_workspace(pid: str, ws: Workspace, folder: Path = PROJECTS_DIR) -> None:
    save(ws, folder / f"{pid}.json")


def delete_workspace(pid: str, folder: Path = PROJECTS_DIR) -> None:
    try:
        (folder / f"{pid}.json").unlink()
    except OSError:
        pass


def save_index(lib: Library, index: Path = INDEX_PATH) -> None:
    try:
        index.parent.mkdir(parents=True, exist_ok=True)
        index.write_text(json.dumps({"order": lib.order, "active": lib.active_id}), encoding="utf-8")
    except OSError:
        pass


def load_library(data_dir: Path = DATA_DIR) -> Optional[Library]:
    """Load every saved project. Falls back to a single-file save from older versions."""
    index, folder, legacy = data_dir / "library.json", data_dir / "projects", data_dir / "workspace.json"
    try:
        meta = json.loads(index.read_text(encoding="utf-8"))
        order = [pid for pid in meta.get("order", []) if load(folder / f"{pid}.json")]
        spaces = {pid: load(folder / f"{pid}.json") for pid in order}
        if spaces:
            return Library(spaces, order, meta.get("active", order[0]))
    except (OSError, ValueError, TypeError):
        pass
    ws = load(legacy)
    return Library.single(ws) if ws else None


def attach(lib: Library, data_dir: Path = DATA_DIR) -> None:
    """Connect autosave and write the current state once."""
    folder = data_dir / "projects"
    lib.on_workspace_change = lambda pid, ws: save_workspace(pid, ws, folder)
    lib.on_index_change = lambda l: save_index(l, data_dir / "library.json")
    for pid, ws in lib.workspaces.items():
        save_workspace(pid, ws, folder)
    save_index(lib, data_dir / "library.json")
