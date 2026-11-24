"""Left navigation rail, built entirely from the workspace."""
import streamlit as st

from components.dialogs import new_item_dialog
from services.formatting import initials
from utils import icons
from utils.actions import create_chat, cycle_accent, navigate
from utils.state import get_page, get_ws
from utils.ui import esc, html

GROUP_ICONS = {"chat": ":material/chat_bubble_outline:", "doc": ":material/description:",
               "map": ":material/account_tree:"}


def nav_key(page: str) -> str:
    return page.replace(":", "_")


def _nav_button(page: str, label: str, icon: str) -> None:
    st.button(label, key=f"nav_{nav_key(page)}", icon=icon,
              type="primary" if get_page() == page else "secondary",
              on_click=navigate, args=(page,), use_container_width=True)


def _group_header(key: str, label: str) -> bool:
    """Header row with a working '+' button. Returns True when '+' was pressed."""
    with st.container(key=f"ghead_{key}"):
        html(f"""
        <div class="a-group">
          <span class="a-group-chev">{icons.chevron_down(12)}</span>
          <span class="a-group-icon">{icons.folder(14)}</span>
          <span class="a-group-label">{label}</span>
        </div>
        """)
        return st.button("New", key=f"add_{key}", icon=":material/add:", help=f"New {label.lower()}")


def render_sidebar() -> None:
    ws = get_ws()
    p = ws.project
    groups = [
        ("chat", "Chat", [(f"chat:{c.id}", c.title) for c in ws.chats]),
        ("doc", "Document", [(d.page, d.title) for d in ws.docs("doc")]),
        ("map", "Map", [(d.page, d.title) for d in ws.docs("map")]),
    ]
    with st.sidebar:
        html(f"""
        <div class="a-project-card">
          <span class="a-project-badge">{esc(initials(p.name))}</span>
          <span class="a-project-text">
            <b>{esc(p.name)}</b>
            <small>{esc(p.engine)} · {esc(p.tagline)}</small>
          </span>
          <span class="a-project-chev">{icons.chevron_right(13)}</span>
        </div>
        """)
        _nav_button("today", "Today", ":material/auto_awesome:")

        for key, label, items in groups:
            if _group_header(key, label):
                if key == "chat":
                    create_chat()
                    st.rerun()
                else:
                    new_item_dialog(key)
            with st.container(key=f"group_{key}"):
                for page, name in items:
                    _nav_button(page, name, GROUP_ICONS[key])

        _nav_button("tasks", "Tasks", ":material/check:")
        _nav_button("changes", "Changes", ":material/history:")

        with st.container(key="side_bottom"):
            html(f"""
            <div class="a-scope-card">
              <div class="a-scope-row"><span>Scope load</span><b>{p.scope_load}%</b></div>
              <div class="a-bar"><i style="width:{p.scope_load}%"></i></div>
              <p>{esc(ws.scope_watch())}</p>
            </div>
            """)
            st.button("Theme", key="side_theme", icon=":material/palette:",
                      on_click=cycle_accent, help="Cycle accent colour", use_container_width=True)
            _nav_button("settings", "Settings", ":material/settings:")
