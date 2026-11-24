"""Glue between a chat, the assistant and the workspace. Pure Python."""
from .assistant import Assistant
from .workspace import Workspace


def send_message(ws: Workspace, assistant: Assistant, chat_id: str, text: str) -> None:
    text = (text or "").strip()
    if not text or not ws.get_chat(chat_id):
        return
    ws.add_message(chat_id, "user", text)
    reply = assistant.reply(ws, chat_id, text)
    for action in reply.actions:
        ws.apply_action(action)
    ws.add_message(chat_id, "alef", reply.text)
