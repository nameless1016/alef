"""Session bootstrap: the workspace, the assistant and navigation."""
import streamlit as st

from services import seed, storage
from services.assistant import get_assistant
from services.workspace import Workspace

DEFAULT_PAGE = "today"


def init_state() -> None:
    if "ws" not in st.session_state:
        ws = storage.load() or seed.default_workspace()
        ws.subscribe(storage.save)
        st.session_state["ws"] = ws
        st.session_state["assistant"] = get_assistant()
    st.session_state.setdefault("page", DEFAULT_PAGE)
    st.session_state.setdefault("editing", set())      # page ids in edit mode
    st.session_state.setdefault("md_open", set())      # map page ids with markdown panel open


def get_ws() -> Workspace:
    return st.session_state["ws"]


def get_assistant_instance():
    return st.session_state["assistant"]


def get_page() -> str:
    return st.session_state.get("page", DEFAULT_PAGE)


def reset_workspace() -> None:
    storage.reset()
    ws = seed.default_workspace()
    ws.subscribe(storage.save)
    st.session_state["ws"] = ws
    st.session_state["page"] = DEFAULT_PAGE
    st.session_state["editing"] = set()
    st.session_state["md_open"] = set()
    storage.save(ws)
