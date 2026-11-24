"""Document screen: rendered view + live editor."""
import streamlit as st

from components.entity_menu import entity_menu
from components.page_header import page_header
from services.markdown_service import to_html
from utils.actions import cancel_edit, save_document, start_edit
from utils.router import entity_id
from utils.state import get_ws
from utils.ui import html


def render(page: str) -> None:
    ws = get_ws()
    doc = ws.get_document(entity_id(page))
    editing = page in st.session_state["editing"]

    page_header(
        "DOCUMENT / LONG DESIGN DOC", doc.title, doc.subtitle,
        primary=(dict(label="Save changes", key=f"save_{doc.id}", tone="solid",
                      icon=":material/save:", on_click=save_document, args=(doc.id, page))
                 if editing else
                 dict(label="Edit long version", key=f"edit_{doc.id}", tone="outline",
                      on_click=start_edit, args=(page,))),
        menu=lambda: entity_menu("doc", doc.id, doc.title),
    )

    if editing:
        with st.container(key="doc_editor"):
            st.text_area("Markdown", value=doc.markdown, height=470, key=f"doc_text_{doc.id}",
                         label_visibility="collapsed")
            st.button("Cancel", key=f"cancel_{doc.id}", on_click=cancel_edit, args=(page,))
        return

    lines = max(12, len(doc.markdown.splitlines()))
    gutter = "".join(f"<span>{i:02d}</span>" for i in range(1, lines + 1))
    html(f"""
    <div class="a-doc">
      <div class="a-gutter">{gutter}</div>
      <div class="a-doc-content">{to_html(doc.markdown)}</div>
    </div>
    """)
