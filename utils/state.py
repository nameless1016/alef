"""Session bootstrap: the project library, the assistant and navigation."""
import streamlit as st

from services import seed, storage
from services.assistant import get_assistant
from services.library import Library
from services.workspace import Workspace

DEFAULT_PAGE = "today"


def init_state() -> None:
    if "lib" not in st.session_state:
        lib = storage.load_library() or Library.single(seed.default_workspace())
        storage.attach(lib)
        st.session_state["lib"] = lib
        st.session_state["assistant"] = get_assistant()
    st.session_state.setdefault("page", DEFAULT_PAGE)
    st.session_state.setdefault("editing", set())      # page ids in edit mode
    st.session_state.setdefault("md_open", set())      # map page ids with markdown panel open
    st.session_state.setdefault("collapsed", set())    # sidebar groups that are collapsed


def get_lib() -> Library:
    return st.session_state["lib"]


def get_ws() -> Workspace:
    return get_lib().active


def get_assistant_instance():
    return st.session_state["assistant"]


def get_page() -> str:
    return st.session_state.get("page", DEFAULT_PAGE)


def _fresh_view() -> None:
    st.session_state["page"] = DEFAULT_PAGE
    st.session_state["editing"] = set()
    st.session_state["md_open"] = set()


def switch_project(pid: str) -> None:
    if get_lib().switch(pid):
        _fresh_view()


def reset_workspace(demo: bool = False) -> None:
    """Replace the active project's contents with a clean slate (or the demo)."""
    old = get_ws().project
    ws = seed.demo_workspace() if demo else seed.default_workspace()
    if not demo:                       # keep this project's identity when clearing
        ws.project.name, ws.project.tagline = old.name, old.tagline
        ws.project.engine, ws.project.user_name = old.engine, old.user_name
    get_lib().replace_active(ws)
    _fresh_view()
