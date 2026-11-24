"""'···' popover: rename + delete for chats, documents and maps."""
import streamlit as st

from utils.actions import delete_entity, rename_entity


def entity_menu(kind: str, entity_id: str, title: str) -> None:
    with st.container(key=f"menu_{entity_id}"):
        with st.popover("Options", icon=":material/more_horiz:"):
            st.text_input("Name", value=title, key=f"rename_{entity_id}")
            st.button("Rename", key=f"rename_btn_{entity_id}", on_click=rename_entity,
                      args=(kind, entity_id), use_container_width=True)
            st.divider()
            sure = st.checkbox("Yes, delete this", key=f"sure_{entity_id}")
            st.button("Delete", key=f"del_btn_{entity_id}", icon=":material/delete:",
                      on_click=delete_entity, args=(kind, entity_id),
                      disabled=not sure, use_container_width=True)
