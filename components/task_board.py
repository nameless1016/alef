"""Kanban board and the 'current focus' rows. Every card is clickable."""
from typing import List

import streamlit as st

from components.dialogs import task_dialog
from services.formatting import fmt_due
from services.models import COLUMNS, Task
from services.workspace import Workspace
from utils import icons
from utils.actions import toggle_task
from utils.state import get_ws
from utils.ui import esc, html


def _card_html(task: Task) -> str:
    cls = " is-done" if task.done else ""
    return f"""
    <div class="a-task{cls}">
      <span class="a-task-main"><b>{esc(task.title)}</b>
      <small>{esc(task.estimate)} · {esc(fmt_due(task.due))}</small></span>
    </div>
    """


def task_card(task: Task) -> None:
    with st.container(key=f"card_task_{task.id}"):
        html(_card_html(task))
        st.button("Toggle complete", key=f"tskchk_{'done_' if task.done else ''}{task.id}",
                  icon=":material/check_box:" if task.done else ":material/check_box_outline_blank:",
                  on_click=toggle_task, args=(task.id,), help="Mark complete / reopen")
        if st.button(f"Open {task.title}", key=f"ovl_task_{task.id}",
                     icon=":material/chevron_right:"):
            task_dialog(task.id)


def render_board(ws: Workspace) -> None:
    with st.container(key="board"):
        cols = st.columns(len(COLUMNS), gap="small")
        for col, (key, label) in zip(cols, COLUMNS):
            items: List[Task] = ws.tasks_in(key)
            with col:
                html(f'<div class="a-col-head"><span>{label.upper()}</span><em>{len(items)}</em></div>')
                with st.container(key=f"colbody_{key}"):
                    for task in items:
                        task_card(task)


def focus_row(index: int, task: Task) -> None:
    tags = task.tags
    tag_html = ""
    if tags:
        tag_html = f'<span class="a-tag a-tag-hot">#{esc(tags[0])}</span>'
        tag_html += "".join(f'<span class="a-tag">#{esc(t)}</span>' for t in tags[1:])
    with st.container(key=f"card_focus_{task.id}"):
        html(f"""
        <div class="a-focus-row">
          <span class="a-focus-num">{index:02d}</span>
          <div class="a-focus-main">
            <b>{esc(task.title)}</b>
            <p>{esc(task.description or 'No notes yet.')}</p>
            <div class="a-focus-meta">{tag_html}
              <span class="a-meta">{icons.clock(12)}{esc(task.estimate)}</span>
              <span class="a-meta">{icons.calendar(12)}{esc(fmt_due(task.due))}</span>
            </div>
          </div>
          <span class="a-prio a-prio-{task.priority}">{task.priority}</span>
        </div>
        """)
        if st.button(f"Open {task.title}", key=f"ovl_focus_{task.id}"):
            task_dialog(task.id)
