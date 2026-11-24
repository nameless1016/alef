"""Today."""
from datetime import datetime

import streamlit as st

from components.buttons import action_button
from components.stats import render_stats
from components.task_board import focus_row
from services.formatting import fmt_long_date, greeting
from utils import icons
from utils.actions import discuss_note, navigate
from utils.state import get_ws
from utils.ui import esc, html


def render() -> None:
    ws = get_ws()
    p, now = ws.project, datetime.now()

    left, right = st.columns([5, 1.3], vertical_alignment="bottom")
    with left:
        html(f"""
        <div class="a-hero">
          <div class="a-eyebrow">{esc(fmt_long_date(now.date()).upper())}</div>
          <h1>{greeting(now.hour)}, {esc(p.user_name)}.</h1>
          <p>{esc(p.goal)}</p>
        </div>
        """)
    with right:
        action_button("Open task board", "go_board", tone="solid", icon=":material/check:",
                      on_click=navigate, args=("tasks",))

    render_stats(ws)

    head, link = st.columns([4, 1], vertical_alignment="bottom")
    with head:
        html("""
        <div class="a-focus-head">
          <div class="a-eyebrow">CURRENT FOCUS</div>
          <h2>Move the uncertainty, not the backlog.</h2>
        </div>
        """)
    with link:
        action_button("View all tasks →", "view_tasks", tone="link", on_click=navigate, args=("tasks",))

    focus = ws.focus_tasks(2)
    with st.container(key="focus_list"):
        if focus:
            for i, task in enumerate(focus, start=1):
                focus_row(i, task)
        else:
            html('<div class="a-empty-box">No current tasks. Every active project keeps at least one: '
                 'add one from the task board.</div>')

    if ws.note:
        with st.container(key="alef_note"):
            note, act = st.columns([9, 1.1], vertical_alignment="center")
            with note:
                html(f"""
                <div class="a-note">
                  <span class="a-note-icon">{icons.sparkle(14)}</span>
                  <div><div class="a-eyebrow">ALEF'S NOTE</div><p>{esc(ws.note)}</p></div>
                </div>
                """)
            with act:
                action_button("Discuss", "discuss", tone="link", on_click=discuss_note)
