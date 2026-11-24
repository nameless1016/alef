"""'···' icon button that opens the rename / delete dialog."""
import streamlit as st

from components.dialogs import entity_dialog


def entity_menu(kind: str, entity_id: str, title: str) -> None:
    with st.container(key=f"menu_{entity_id}"):
        if st.button("Options", key=f"menu_btn_{entity_id}", icon=":material/more_horiz:"):
            entity_dialog(kind, entity_id, title)
