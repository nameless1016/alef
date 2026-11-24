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
    chat_service.send_message(get_ws(), get_assistant_instance(), chat_id, text)


def send_chip(chat_id: str, text: str) -> None:
    chat_service.send_message(get_ws(), get_assistant_instance(), chat_id, text)


def discuss_note() -> None:
    ws = get_ws()
    chat = ws.get_chat("scope") or (ws.chats[0] if ws.chats else ws.new_chat("Scope review"))
    ws.add_message(chat.id, "alef", f"Picking up my note from Today: {ws.note}")
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


# ---- changes / theme
def update_alef() -> None:
    snap = get_ws().sync_context()
    st.toast(f"Alef context updated: {len(snap['tasks'])} tasks, "
             f"{len(snap['documents']) + len(snap['maps'])} files")


def cycle_accent() -> None:
    from services.models import ACCENTS
    ws = get_ws()
    names = list(ACCENTS)
    ws.project.accent = names[(names.index(ws.project.accent) + 1) % len(names)]
    ws._touch()
    st.toast(f"Accent: {ws.project.accent}")
