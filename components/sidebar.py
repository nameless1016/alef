"""Left navigation rail."""
import streamlit as st

from services.data_service import NAV_GROUPS, PROJECT, SCOPE_NOTE
from utils import icons
from utils.state import get_page, navigate
from utils.ui import html

ITEM_ICONS = {
    "chat": ":material/chat_bubble_outline:",
    "doc": ":material/description:",
    "map": ":material/account_tree:",
}


def nav_key(page: str) -> str:
    return page.replace(":", "_")


def _nav_button(page: str, label: str, icon: str) -> None:
    st.button(
        label,
        key=f"nav_{nav_key(page)}",
        icon=icon,
        type="primary" if get_page() == page else "secondary",
        on_click=navigate,
        args=(page,),
        use_container_width=True,
    )


def _toast_theme() -> None:
    st.toast("Only the dark theme is available in this build.")


def render_sidebar() -> None:
    with st.sidebar:
        html(f"""
        <div class="a-project-card">
          <span class="a-project-badge">{PROJECT['initials']}</span>
          <span class="a-project-text">
            <b>{PROJECT['name']}</b>
            <small>{PROJECT['engine']} · {PROJECT['tagline']}</small>
          </span>
          <span class="a-project-chev">{icons.chevron_right(13)}</span>
        </div>
        """)

        _nav_button("today", "Today", ":material/auto_awesome:")

        for group in NAV_GROUPS:
            plus = '<span class="a-group-plus">+</span>' if group.get("action") else ""
            html(f"""
            <div class="a-group">
              <span class="a-group-chev">{icons.chevron_down(12)}</span>
              <span class="a-group-icon">{icons.folder(14)}</span>
              <span class="a-group-label">{group['label']}</span>{plus}
            </div>
            """)
            with st.container(key=f"group_{group['key']}"):
                for page, label in group["items"]:
                    _nav_button(page, label, ITEM_ICONS[group["key"]])

        _nav_button("tasks", "Tasks", ":material/check:")
        _nav_button("changes", "Changes", ":material/history:")

        with st.container(key="side_bottom"):
            html(f"""
            <div class="a-scope-card">
              <div class="a-scope-row"><span>Scope load</span><b>{PROJECT['scope_load']}%</b></div>
              <div class="a-bar"><i style="width:{PROJECT['scope_load']}%"></i></div>
              <p>{SCOPE_NOTE}</p>
            </div>
            """)
            st.button("Theme", key="side_theme", icon=":material/palette:",
                      on_click=_toast_theme, use_container_width=True)
            _nav_button("settings", "Settings", ":material/settings:")
