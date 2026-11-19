"""Today screen."""
import streamlit as st

from components.task_card import focus_row
from services.data_service import (ALEF_NOTE, FOCUS_TASK_IDS, MILESTONE, PROJECT,
                                   SCOPE_HEALTH, task_by_id)
from utils import icons
from utils.state import navigate
from utils.ui import html


def render() -> None:
    left, right = st.columns([5, 1.25], vertical_alignment="bottom")
    with left:
        html(f"""
        <div class="a-hero">
          <div class="a-eyebrow">{PROJECT['today_label'].upper()}</div>
          <h1>Good morning, {PROJECT['user_name']}.</h1>
          <p>{PROJECT['goal']}</p>
        </div>
        """)
    with right:
        with st.container(key="hdr_solid_open_board"):
            st.button("Open task board", key="open_board", icon=":material/check:",
                      on_click=navigate, args=("tasks",))

    m = MILESTONE
    html(f"""
    <div class="a-stats">
      <div class="a-stat">
        <div class="a-eyebrow">PROJECT PROGRESS</div>
        <div class="a-progress">
          <div class="a-progress-num"><b>{PROJECT['progress']}%</b><small>SLICE</small></div>
          <div class="a-progress-text">
            <h3>{PROJECT['name']}</h3>
            <p>{PROJECT['description']}</p>
            <span class="a-amber">Target · {PROJECT['target']}</span>
          </div>
        </div>
      </div>
      <div class="a-stat">
        <div class="a-eyebrow">SCOPE HEALTH</div>
        <div class="a-health"><span class="a-diamond">◆</span>{SCOPE_HEALTH['label']}</div>
        <p class="a-muted">{SCOPE_HEALTH['text']}</p>
        <div class="a-budget">
          <div class="a-scope-row"><span>Budget used</span><b>{PROJECT['budget_used']}%</b></div>
          <div class="a-bar"><i style="width:{PROJECT['budget_used']}%"></i></div>
        </div>
      </div>
      <div class="a-stat">
        <div class="a-eyebrow">NEXT MILESTONE</div>
        <div class="a-month">{m['month'].upper()}</div>
        <div class="a-day">{m['day']}</div>
        <h3>{m['title']}</h3>
        <p class="a-dim">{m['meta']}</p>
      </div>
    </div>
    """)

    head, link = st.columns([4, 1], vertical_alignment="bottom")
    with head:
        html("""
        <div class="a-focus-head">
          <div class="a-eyebrow">CURRENT FOCUS</div>
          <h2>Move the uncertainty, not the backlog.</h2>
        </div>
        """)
    with link:
        with st.container(key="hdr_link_view_tasks"):
            st.button("View all tasks →", key="view_tasks", on_click=navigate, args=("tasks",))

    rows = "".join(focus_row(i + 1, task_by_id(tid)) for i, tid in enumerate(FOCUS_TASK_IDS))
    html(f'<div class="a-focus-list">{rows}</div>')

    with st.container(key="alef_note"):
        note, act = st.columns([9, 1], vertical_alignment="center")
        with note:
            html(f"""
            <div class="a-note">
              <span class="a-note-icon">{icons.sparkle(14)}</span>
              <div><div class="a-eyebrow">ALEF'S NOTE</div><p>{ALEF_NOTE}</p></div>
            </div>
            """)
        with act:
            with st.container(key="hdr_link_discuss"):
                st.button("Discuss", key="discuss", on_click=navigate, args=("chat:vertical",))
