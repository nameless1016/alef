"""Alef: entrypoint. Page config, CSS injection and routing."""
import streamlit as st
from PIL import Image

from components.chrome import render_statusbar, render_topbar
from components.sidebar import render_sidebar
from utils.router import resolve
from utils.state import get_page, get_ws, init_state
from utils.ui import LOGO_PATH, inject_css
from views import changes, chat, document, home, markmap, settings, tasks

st.set_page_config(page_title="Alef", page_icon=Image.open(LOGO_PATH), layout="wide",
                   initial_sidebar_state="expanded")

init_state()
ws = get_ws()
page = resolve(get_page())
st.session_state["page"] = page

WIDTHS = {"tasks": 963}
inject_css(
    content_width=WIDTHS.get(page, 835),
    badges={"tasks": len(ws.open_tasks()), "changes": ws.unsynced_count()},
    accent=ws.project.accent,
    full_bleed=page.startswith("chat:"),
)

render_topbar()
render_sidebar()
render_statusbar()

kind = page.partition(":")[0]
if page == "today":
    home.render()
elif kind == "chat":
    chat.render(page)
elif kind == "doc":
    document.render(page)
elif kind == "map":
    markmap.render(page)
elif page == "tasks":
    tasks.render()
elif page == "changes":
    changes.render()
elif page == "settings":
    settings.render()
