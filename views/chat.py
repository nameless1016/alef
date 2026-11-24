"""Chat screen."""
from components.chat_view import render_composer, render_header, render_messages
from utils.router import entity_id
from utils.state import get_ws


def render(page: str) -> None:
    ws = get_ws()
    chat = ws.get_chat(entity_id(page))
    render_header(chat)
    render_messages(chat, ws.project.user_name[:2].upper())
    render_composer(ws, chat)
