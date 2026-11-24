"""Document screen: rendered view + live editor."""
import re

import streamlit as st

from components.entity_menu import entity_menu
from components.page_header import page_header
from services.assistant import is_live_ai
from services.markdown_service import to_html
from utils.actions import cancel_edit, recontextualize_document, save_document, start_edit
from utils.router import entity_id
from utils.state import get_assistant_instance, get_ws
from utils.ui import html


def render(page: str) -> None:
    ws = get_ws()
    doc = ws.get_document(entity_id(page))
    editing = page in st.session_state["editing"]
    is_short = doc.role == "short" or (doc.role is None and doc.title.strip().lower() == "project brief")
    eyebrow = "DOCUMENT / SHORT SUMMARY" if is_short else "DOCUMENT / LONG DESIGN DOC"
    edit_label = "Edit short summary" if is_short else "Edit long version"

    page_header(
        eyebrow, doc.title, doc.subtitle,
        primary=(dict(label="Save changes", key=f"save_{doc.id}", tone="solid",
                      icon=":material/save:", on_click=save_document, args=(doc.id, page))
                 if editing else
                 dict(label=edit_label, key=f"edit_{doc.id}", tone="outline",
                      on_click=start_edit, args=(page,))),
        menu=lambda: entity_menu("doc", doc.id, doc.title),
    )

    if is_short:
        words = len(re.findall(r"\S+", doc.markdown or ""))
        st.caption(f"Core memory length: {words} / 300 words")
    elif not editing:
        live = is_live_ai(get_assistant_instance())
        can_rectx = live and ws.is_initialized() and bool(doc.markdown.strip())
        st.button(
            "Recontextualize Short Doc",
            key=f"rectx_{doc.id}",
            icon=":material/auto_awesome:",
            on_click=recontextualize_document,
            args=(doc.id,),
            disabled=not can_rectx,
            help=("Ask Alef to refresh your Short Summary (< 300 words) from this Long Document."
                  if live else "Set ALEF_API_KEY in .env to enable AI recontextualization."),
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
