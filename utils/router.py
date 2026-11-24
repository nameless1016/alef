"""Page ids look like 'today', 'tasks' or '<kind>:<id>' (chat/doc/map)."""
from utils.state import get_ws

STATIC_PAGES = {"today", "tasks", "changes", "settings"}


def resolve(page: str) -> str:
    """Fall back to Today when a page points at something that was deleted."""
    if page in STATIC_PAGES:
        return page
    kind, _, entity_id = page.partition(":")
    ws = get_ws()
    exists = {
        "chat": ws.get_chat,
        "doc": ws.get_document,
        "map": ws.get_document,
    }.get(kind)
    return page if exists and exists(entity_id) else "today"


def entity_id(page: str) -> str:
    return page.partition(":")[2]
