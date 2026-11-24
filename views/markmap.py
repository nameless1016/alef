"""Mind-map screen: live map + editable markdown panel."""
import streamlit as st

from components.entity_menu import entity_menu
from components.mindmap import render_mindmap
from components.page_header import page_header
from utils import icons
from utils.actions import save_map_markdown, toggle_markdown
from utils.router import entity_id
from utils.state import get_ws
from utils.ui import esc, html


def render(page: str) -> None:
    ws = get_ws()
    doc = ws.get_document(entity_id(page))
    visible = page in st.session_state["md_open"]

    page_header(
        "MARKMAP / " + doc.title.upper(), doc.title, doc.subtitle,
        primary=dict(label="Hide markdown" if visible else "View markdown",
                     key=f"toggle_md_{doc.id}", tone="outline",
                     on_click=toggle_markdown, args=(page,)),
        menu=lambda: entity_menu("map", doc.id, doc.title),
    )

    with st.container(key="markmap_split"):
        if visible:
            left, right = st.columns([1, 1.95], gap="small")
            with left:
                with st.container(key="md_editor"):
                    html(f'<div class="a-md-file">{icons.file(13)}{esc(doc.filename)}</div>')
                    st.text_area("Markdown", value=doc.markdown, height=460, key=f"map_md_{doc.id}",
                                 on_change=save_map_markdown, args=(doc.id,),
                                 label_visibility="collapsed",
                                 help="Edits update the map when you click outside the box.")
                    html('<div class="a-md-hint"># root &nbsp;·&nbsp; ## branch &nbsp;·&nbsp; ### sub-branch '
                         '&nbsp;·&nbsp; Ctrl+Enter to apply</div>')
            with right:
                render_mindmap(doc.markdown)
        else:
            render_mindmap(doc.markdown)
