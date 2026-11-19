"""Alef: entrypoint. Page config, CSS injection and routing."""
import streamlit as st
from PIL import Image

from components.chrome import render_statusbar, render_topbar
from components.sidebar import render_sidebar
from services.data_service import change_count, open_task_count
from utils.state import get_page, init_state
from utils.ui import LOGO_PATH, inject_css
from views import changes, chat, document, home, markmap, settings, tasks

st.set_page_config(page_title="Alef · Glasshouse Protocol",
                   page_icon=Image.open(LOGO_PATH), layout="wide",
                   initial_sidebar_state="expanded")

init_state()
page = get_page()

# page -> (render function, content width in px, full-bleed?)
WIDTHS = {"tasks": 963, "settings": 835}
FULL_BLEED = page.startswith("chat:")

inject_css(
    content_width=WIDTHS.get(page, 835),
    badges={"tasks": open_task_count(), "changes": change_count()},
    full_bleed=FULL_BLEED,
)

render_topbar()
render_sidebar()
render_statusbar()

if page == "today":
    home.render()
elif page.startswith("chat:"):
    chat.render(page)
elif page.startswith("doc:"):
    document.render(page)
elif page.startswith("map:"):
    markmap.render(page)
elif page == "tasks":
    tasks.render()
elif page == "changes":
    changes.render()
elif page == "settings":
    settings.render()
else:
    home.render()
