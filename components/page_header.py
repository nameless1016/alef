"""Standard page header with an optional primary action and options menu."""
from typing import Callable, Optional

import streamlit as st

from components.buttons import action_button
from utils.ui import esc, html


def page_header(eyebrow: str, title: str, subtitle: str,
                primary: Optional[dict] = None,
                menu: Optional[Callable[[], None]] = None) -> bool:
    """Returns True when the primary button was pressed (for dialog-opening actions)."""
    with st.container(key="page_head"):
        # Title takes the free space; the actions hug the right edge (see .st-key-page_head in styles.css).
        cols = st.columns(1 + bool(menu) + bool(primary), vertical_alignment="top")
        with cols[0]:
            html(f"""
            <div class="a-header">
              <div class="a-eyebrow">{esc(eyebrow)}</div>
              <h2 class="a-title">{esc(title)}</h2>
              <p class="a-subtitle">{esc(subtitle)}</p>
            </div>
            """)
        clicked, i = False, 1
        if menu:
            with cols[i]:
                menu()
            i += 1
        if primary:
            with cols[i]:
                clicked = action_button(**primary)
    html('<div class="a-rule"></div>')
    return clicked
