"""One button wrapper so every styled button is declared the same way."""
from typing import Callable, Optional

import streamlit as st

TONES = ("outline", "solid", "link")


def action_button(label: str, key: str, tone: str = "outline", icon: Optional[str] = None,
                  on_click: Optional[Callable] = None, args: tuple = (),
                  disabled: bool = False) -> bool:
    """Styled button; the wrapper's class `st-key-btn_<tone>_<key>` drives the CSS."""
    with st.container(key=f"btn_{tone}_{key}"):
        return st.button(label, key=key, icon=icon, on_click=on_click, args=args,
                         disabled=disabled)
