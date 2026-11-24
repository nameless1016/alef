"""UI callbacks. Each one is a thin wrapper over a Workspace method."""
import streamlit as st

from services import chat_service
from utils.state import get_assistant_instance, get_ws


def navigate(page: str) -> None:
    st.session_state["page"] = page


# ---- tasks
def toggle_task(task_id: str) -> None:
    ws = get_ws()
    task = ws.get_task(task_id)
    ws.toggle_done(task_id)
    if task:
        st.toast("Reopened" if task.done else "Marked complete")


# ---- chats
def create_chat() -> None:
    chat = get_ws().new_chat()
    navigate(f"chat:{chat.id}")


def send_chat_input(chat_id: str) -> None:
    text = st.session_state.get(f"chat_input_{chat_id}", "")
    reply = chat_service.send_message(get_ws(), get_assistant_instance(), chat_id, text)
    if reply and reply.warnings:
        st.toast(reply.warnings[0])


def send_chip(chat_id: str, text: str) -> None:
    reply = chat_service.send_message(get_ws(), get_assistant_instance(), chat_id, text)
    if reply and reply.warnings:
        st.toast(reply.warnings[0])


def discuss_note() -> None:
    """Open a chat and send the note as *your* message (Alef never speaks first)."""
    ws = get_ws()
    chat = ws.chats[0] if ws.chats else ws.new_chat("Scope review")
    chat_service.send_message(ws, get_assistant_instance(), chat.id, f"Let's discuss: {ws.note}")
    navigate(f"chat:{chat.id}")


def rename_entity(kind: str, entity_id: str) -> None:
    ws = get_ws()
    name = st.session_state.get(f"rename_{entity_id}", "")
    if kind == "chat":
        ws.rename_chat(entity_id, name)
    else:
        ws.update_document(entity_id, title=name)
    st.toast("Renamed")


def delete_entity(kind: str, entity_id: str) -> None:
    ws = get_ws()
    if kind == "chat":
        ws.delete_chat(entity_id)
    else:
        ws.delete_document(entity_id)
    st.session_state["editing"].discard(f"{kind}:{entity_id}")
    navigate("today")
    st.toast("Deleted")


# ---- documents & maps
def start_edit(page: str) -> None:
    st.session_state["editing"].add(page)


def cancel_edit(page: str) -> None:
    st.session_state["editing"].discard(page)


def save_document(doc_id: str, page: str) -> None:
    get_ws().update_document(doc_id, markdown=st.session_state.get(f"doc_text_{doc_id}", ""))
    st.session_state["editing"].discard(page)
    st.toast("Document saved")


def toggle_markdown(page: str) -> None:
    s = st.session_state["md_open"]
    s.symmetric_difference_update({page})


def save_map_markdown(doc_id: str) -> None:
    get_ws().update_document(doc_id, markdown=st.session_state.get(f"map_md_{doc_id}", ""))


# ---- changes / AI actions / theme
def update_alef() -> None:
    from services.assistant import is_live_ai

    ws = get_ws()
    assistant = get_assistant_instance()
    chat_id, reply = chat_service.sync_with_alef(ws, assistant)
    if reply.is_error:
        st.toast(reply.text)
        return
    if is_live_ai(assistant) and chat_id:
        st.toast("Alef reviewed your changes")
        navigate(f"chat:{chat_id}")
    else:
        snap = ws.context_snapshot()
        st.toast(f"Alef context updated: {len(snap['tasks'])} tasks, "
                 f"{len(snap['documents']) + len(snap['maps'])} files")


def recontextualize_document(doc_id: str) -> None:
    ws = get_ws()
    reply = chat_service.recontextualize_doc(ws, get_assistant_instance(), doc_id)
    if reply.is_error or not reply.actions:
        st.toast(reply.text)
        return
    if reply.warnings:
        st.toast(reply.warnings[0])
    else:
        st.toast("Short Document updated from Long Document")
    short = ws.short_doc()
    if short:
        navigate(short.page)


def unlock_workspace() -> None:
    ws = get_ws()
    ws.project.initialized = True
    ws._touch()
    st.toast("Workspace unlocked")


def cycle_accent() -> None:
    from services.models import ACCENTS
    ws = get_ws()
    names = list(ACCENTS)
    ws.project.accent = names[(names.index(ws.project.accent) + 1) % len(names)]
    ws._touch()
    st.toast(f"Accent: {ws.project.accent}")


def toggle_group(key: str) -> None:
    st.session_state["collapsed"].symmetric_difference_update({key})
