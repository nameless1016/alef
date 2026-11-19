"""Mind-map screens."""
import streamlit as st

from components.mindmap import render_mindmap
from components.page_header import page_header
from services.data_service import MAPS
from utils import icons
from utils.state import markdown_visible, toggle_markdown
from utils.ui import html


def _markdown_panel(filename: str, markdown: str) -> str:
    lines = "".join(
        f'<div><i>{n:02d}</i><span>{line}</span></div>'
        for n, line in enumerate(markdown.splitlines(), start=1)
    )
    return f"""
    <div class="a-md-panel">
      <div class="a-md-file">{icons.file(13)}{filename}</div>
      <div class="a-md-lines">{lines}</div>
    </div>
    """


def render(map_key: str) -> None:
    data = MAPS[map_key]
    visible = markdown_visible(map_key)
    page_header(data["eyebrow"].upper(), data["title"], data["subtitle"],
                action="Hide markdown" if visible else "View markdown",
                action_key=f"toggle_md_{map_key.replace(':', '_')}",
                on_click=toggle_markdown, args=(map_key,))
    with st.container(key="markmap_split"):
        if visible:
            left, right = st.columns([1, 1.95], gap="small")
            with left:
                html(_markdown_panel(data["filename"], data["markdown"]))
            with right:
                render_mindmap(data["markdown"])
        else:
            render_mindmap(data["markdown"])
