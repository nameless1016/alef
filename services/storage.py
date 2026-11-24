"""JSON persistence for the workspace. Pure Python."""
import json
from pathlib import Path
from typing import Optional

from .workspace import Workspace

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
        return Workspace.from_dict(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError, TypeError):
        return None


def reset(path: Path = DATA_PATH) -> None:
    try:
        path.unlink()
    except OSError:
        pass
