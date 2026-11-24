"""Glue between chats, the assistant, and the workspace. Pure Python."""
from typing import Optional, Tuple

from .assistant import AlefAssistant, Assistant, AssistantReply, is_live_ai
from .workspace import Workspace


def send_message(ws: Workspace, assistant: Assistant, chat_id: str, text: str) -> Optional[AssistantReply]:
    text = (text or "").strip()
    if not text or not ws.get_chat(chat_id):
        return None
    ws.add_message(chat_id, "user", text)
    reply = assistant.reply(ws, chat_id, text)
    if not reply.is_error:
        for action in reply.actions:
            ws.apply_action(action, source="ai")
        if reply.synced_changes:
            ws.sync_context()
    ws.add_message(chat_id, "alef", reply.text)
    return reply


def sync_with_alef(
    ws: Workspace,
    assistant: Assistant,
    chat_id: Optional[str] = None,
) -> Tuple[Optional[str], AssistantReply]:
    """Run the Change-Sync Gate: send pending changes to Alef and mark synced on success."""
    if not is_live_ai(assistant):
        ws.sync_context()
        return chat_id, AssistantReply("Alef context updated locally.", synced_changes=True)

    assert isinstance(assistant, AlefAssistant)
    chat = ws.get_chat(chat_id) if chat_id else (ws.chats[-1] if ws.chats else ws.new_chat("Context sync"))
    if chat is None:
        chat = ws.new_chat("Context sync")

    reply = assistant.sync_changes(ws, chat.id)
    if not reply.is_error:
        for action in reply.actions:
            ws.apply_action(action, source="ai")
        ws.sync_context()
        ws.add_message(chat.id, "alef", reply.text)
    return chat.id, reply


def recontextualize_doc(
    ws: Workspace,
    assistant: Assistant,
    doc_id: str,
    chat_id: Optional[str] = None,
) -> AssistantReply:
    """Refresh Short Doc from a read-only Long Document via Alef."""
    if not is_live_ai(assistant):
        return AssistantReply(
            text="Connect ALEF_API_KEY to recontextualize the Short Document from a Long Document.",
            is_error=True,
        )

    assert isinstance(assistant, AlefAssistant)
    reply = assistant.recontextualize(ws, doc_id, chat_id=chat_id)
    if not reply.is_error:
        for action in reply.actions:
            ws.apply_action(action, source="ai")
        chat = ws.get_chat(chat_id) if chat_id else (ws.chats[-1] if ws.chats else None)
        if chat is not None:
            ws.add_message(chat.id, "alef", reply.text)
    return reply
