"""Standard page header: eyebrow, title, subtitle and an optional action button."""
from typing import Callable, Optional

import streamlit as st

from utils.ui import html


def page_header(eyebrow: str, title: str, subtitle: str,
                action: Optional[str] = None, action_key: str = "page_action",
                icon: Optional[str] = None, on_click: Optional[Callable] = None,
                args: tuple = (), tone: str = "outline") -> None:
    left, right = st.columns([5, 1.4], vertical_alignment="top")
    with left:
        html(f"""
        <div class="a-header">
          <div class="a-eyebrow">{eyebrow}</div>
          <h2 class="a-title">{title}</h2>
          <p class="a-subtitle">{subtitle}</p>
        </div>
        """)
    with right:
        if action:
            with st.container(key=f"hdr_{tone}_{action_key}"):
                st.button(action, key=action_key, icon=icon,
                          on_click=on_click, args=args)
    html('<div class="a-rule"></div>')
