"""Settings screen (layout only; values are not persisted)."""
import streamlit as st

from components.page_header import page_header
from services.data_service import PROJECT, SETTINGS_FIELDS
from utils.ui import html


def render() -> None:
    page_header("WORKSPACE / SETTINGS", "Settings",
                "Project details and how Alef reads your files.")
    with st.container(key="settings_form"):
        html('<div class="a-eyebrow a-section">PROJECT</div>')
        st.text_input("Project name", value=PROJECT["name"])
        st.text_area("Description", value=PROJECT["description"], height=80)
        st.selectbox("Engine", SETTINGS_FIELDS["engines"], index=0)
        html('<div class="a-eyebrow a-section">ALEF</div>')
        st.toggle("Include documents in context", value=True)
        st.toggle("Include maps in context", value=True)
        st.toggle("Ask before adding tasks", value=False)
