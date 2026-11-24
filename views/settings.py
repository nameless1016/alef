"""Settings: every field writes straight to the workspace."""
from datetime import date

import streamlit as st

from components.page_header import page_header
from services.models import ACCENTS, ENGINES
from utils.state import get_ws, reset_workspace
from utils.ui import html


def _d(iso: str, fallback: date) -> date:
    return date.fromisoformat(iso) if iso else fallback


def render() -> None:
    ws = get_ws()
    p = ws.project
    page_header("WORKSPACE / SETTINGS", "Settings", "Project details and how Alef reads your files.")

    with st.container(key="settings_form"):
        with st.form("settings"):
            html('<div class="a-eyebrow a-section">YOU</div>')
            user_name = st.text_input("Your name", value=p.user_name)
            html('<div class="a-eyebrow a-section">PROJECT</div>')
            name = st.text_input("Project name", value=p.name)
            tagline = st.text_input("Tagline", value=p.tagline)
            description = st.text_area("Description", value=p.description, height=80)
            goal = st.text_area("Goal shown on Today", value=p.goal, height=80)
            c1, c2 = st.columns(2)
            engine = c1.selectbox("Engine", ENGINES,
                                  index=ENGINES.index(p.engine) if p.engine in ENGINES else 0)
            branch = c2.text_input("Branch", value=p.branch)
            c3, c4 = st.columns(2)
            target = c3.date_input("Target date", value=_d(p.target, date.today()))
            m_date = c4.date_input("Next milestone date", value=_d(p.milestone_date, date.today()))
            m_title = st.text_input("Next milestone", value=p.milestone_title)
            html('<div class="a-eyebrow a-section">HEALTH</div>')
            scope_load = st.slider("Scope load", 0, 100, p.scope_load, format="%d%%")
            budget = st.slider("Budget used", 0, 100, p.budget_used, format="%d%%")
            baseline = st.slider("Work done before tasks were tracked", 0, 90, p.baseline,
                                 format="%d%%", help="Added to the progress calculated from tasks.")
            html('<div class="a-eyebrow a-section">ALEF</div>')
            inc_docs = st.toggle("Include documents in context", value=p.include_docs)
            inc_maps = st.toggle("Include maps in context", value=p.include_maps)
            accent = st.selectbox("Accent colour", list(ACCENTS), index=list(ACCENTS).index(p.accent))
            saved = st.form_submit_button("Save settings", type="primary")

        if saved:
            p.user_name, p.name, p.tagline = user_name.strip() or p.user_name, name.strip() or p.name, tagline
            p.description, p.goal, p.engine, p.branch = description, goal, engine, branch
            p.target, p.milestone_date, p.milestone_title = target.isoformat(), m_date.isoformat(), m_title
            p.scope_load, p.budget_used, p.baseline = scope_load, budget, baseline
            p.include_docs, p.include_maps, p.accent = inc_docs, inc_maps, accent
            ws._touch()
            st.toast("Settings saved")
            st.rerun()

        html('<div class="a-eyebrow a-section">DATA</div>')
        with st.popover("Clear all data"):
            st.write("This removes every task, chat, document and change.")
            st.button("Yes, clear everything", on_click=reset_workspace, type="primary", key="clear_all")
        with st.popover("Load demo data"):
            st.write("This replaces everything with the Glasshouse Protocol demo content.")
            st.button("Yes, load the demo", on_click=reset_workspace, args=(True,), type="primary", key="load_demo")
