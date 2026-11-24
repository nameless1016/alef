"""Left navigation rail, built entirely from the workspace."""
import streamlit as st

from components.dialogs import new_item_dialog, project_dialog
from services.assistant import is_live_ai
from services.formatting import initials
from utils import icons
from utils.actions import create_chat, cycle_accent, navigate, toggle_group
from utils.state import get_assistant_instance, get_lib, get_page, get_ws
from utils.ui import esc, html

GROUP_ICONS = {"chat": ":material/chat_bubble_outline:", "doc": ":material/description:",
               "map": ":material/account_tree:"}


def nav_key(page: str) -> str:
    return page.replace(":", "_")


def _nav_button(page: str, label: str, icon: str, disabled: bool = False) -> None:
    st.button(label, key=f"nav_{nav_key(page)}", icon=icon,
              type="primary" if get_page() == page else "secondary",
              on_click=navigate, args=(page,), use_container_width=True, disabled=disabled)


def _group_header(key: str, label: str, collapsed: bool, disabled: bool = False) -> bool:
    """Collapsible header row with a working '+'. Returns True when '+' was pressed."""
    chev = icons.chevron_right(12) if collapsed else icons.chevron_down(12)
    with st.container(key=f"ghead_{key}"):
        html(f"""
        <div class="a-group">
          <span class="a-group-chev">{chev}</span>
          <span class="a-group-icon">{icons.folder(14)}</span>
          <span class="a-group-label">{label}</span>
        </div>
        """)
        st.button(f"Toggle {label}", key=f"gtoggle_{key}", on_click=toggle_group, args=(key,), disabled=disabled)
        return st.button("New", key=f"add_{key}", icon=":material/add:", disabled=disabled)


def _project_card() -> None:
    p = get_ws().project
    with st.container(key="card_project"):
        html(f"""
        <div class="a-project-card">
          <span class="a-project-badge">{esc(initials(p.name))}</span>
          <span class="a-project-text">
            <b>{esc(p.name)}</b>
            <small>{esc(p.engine)}{' · ' + esc(p.tagline) if p.tagline else ''}</small>
          </span>
          <span class="a-project-chev">{icons.chevron_right(13)}</span>
        </div>
        """)
        if st.button("Switch project", key="ovl_project"):
            project_dialog()


def render_sidebar() -> None:
    ws = get_ws()
    p = ws.project
    locked = is_live_ai(get_assistant_instance()) and not ws.is_initialized()
    collapsed = st.session_state["collapsed"]
    groups = [
        ("chat", "Chat", [(f"chat:{c.id}", c.title) for c in ws.chats]),
        ("doc", "Document", [(d.page, d.title) for d in ws.docs("doc")]),
        ("map", "Map", [(d.page, d.title) for d in ws.docs("map")]),
    ]
    with st.sidebar:
        _project_card()
        _nav_button("today", "Today", ":material/auto_awesome:")

        for key, label, items in groups:
            is_collapsed = key in collapsed
            group_locked = locked and key in ("doc", "map")
            if _group_header(key, label, is_collapsed, disabled=group_locked):
                if key == "chat":
                    create_chat()
                    collapsed.discard("chat")
                    st.rerun()
                else:
                    collapsed.discard(key)
                    new_item_dialog(key)
            if not is_collapsed and not group_locked:
                with st.container(key=f"group_{key}"):
                    for page, name in items:
                        _nav_button(page, name, GROUP_ICONS[key])

        _nav_button("tasks", "Tasks", ":material/check:", disabled=locked)
        _nav_button("changes", "Changes", ":material/history:", disabled=locked)
        if locked:
            st.caption("Complete project setup in Chat to unlock Documents, Map, Tasks & Changes.")

        with st.container(key="side_bottom"):
            if ws.tasks or p.scope_load:
                html(f"""
                <div class="a-scope-card">
                  <div class="a-scope-row"><span>Scope load</span><b>{p.scope_load}%</b></div>
                  <div class="a-bar"><i style="width:{p.scope_load}%"></i></div>
                  <p>{esc(ws.scope_watch())}</p>
                </div>
                """)
            st.button("Theme", key="side_theme", icon=":material/palette:",
                      on_click=cycle_accent, use_container_width=True)
            _nav_button("settings", "Settings", ":material/settings:")
