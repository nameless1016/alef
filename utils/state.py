"""Session-state helpers (navigation + small UI toggles)."""
import streamlit as st

DEFAULT_PAGE = "today"


def init_state() -> None:
    st.session_state.setdefault("page", DEFAULT_PAGE)
    st.session_state.setdefault("show_markdown", {})   # map key -> bool
    st.session_state.setdefault("chat_extra", {})      # chat key -> [(role, text)]


def get_page() -> str:
    return st.session_state.get("page", DEFAULT_PAGE)


def navigate(page: str) -> None:
    st.session_state["page"] = page


def toggle_markdown(map_key: str) -> None:
    flags = st.session_state["show_markdown"]
    flags[map_key] = not flags.get(map_key, False)


def markdown_visible(map_key: str) -> bool:
    return st.session_state["show_markdown"].get(map_key, False)


def submit_chat(chat_key: str) -> None:
    """UI-only: echo the typed text as a user bubble. No reply logic yet."""
    text = st.session_state.get("chat_input", "").strip()
    if not text:
        return
    st.session_state["chat_extra"].setdefault(chat_key, []).append(("user", text))
    st.session_state["chat_input"] = ""


def use_suggestion(chat_key: str, text: str) -> None:
    st.session_state["chat_extra"].setdefault(chat_key, []).append(("user", text))
