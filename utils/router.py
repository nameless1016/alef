"""Page ids look like 'today', 'tasks' or '<kind>:<id>' (chat/doc/map)."""
from services.assistant import is_live_ai
from services.workspace import Workspace
from utils.state import get_assistant_instance, get_ws

STATIC_PAGES = {"today", "tasks", "changes", "settings"}
LOCKED_STATIC = {"tasks", "changes"}
LOCKED_KINDS = {"doc", "map"}


def is_page_locked(page: str, ws: Workspace, live_ai: bool) -> bool:
    """Lock non-chat project tabs until `<project_init>` unlocks them (live AI only)."""
    if not live_ai or ws.is_initialized():
        return False
    if page in LOCKED_STATIC:
        return True
    kind = page.partition(":")[0]
    return kind in LOCKED_KINDS


def resolve(page: str) -> str:
    """Fall back to starter chat when locked, or Today when a page was deleted."""
    ws = get_ws()
    live_ai = is_live_ai(get_assistant_instance())
    if is_page_locked(page, ws, live_ai):
        chat = ws.chats[0] if ws.chats else ws.new_chat("Project setup")
        return f"chat:{chat.id}"
    if page in STATIC_PAGES:
        return page
    kind, _, entity_id = page.partition(":")
    exists = {
        "chat": ws.get_chat,
        "doc": ws.get_document,
        "map": ws.get_document,
    }.get(kind)
    return page if exists and exists(entity_id) else "today"


def entity_id(page: str) -> str:
    return page.partition(":")[2]
