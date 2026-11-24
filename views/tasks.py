"""Task board screen."""
from components.dialogs import task_dialog
from components.page_header import page_header
from components.task_board import render_board
from utils.state import get_ws


def render() -> None:
    ws = get_ws()
    m = ws.milestone()
    days = f" / {m['days_left']} DAYS LEFT" if m["days_left"] is not None else ""
    if page_header(f"SPRINT 03{days}", "Task board",
                   "Every active project keeps at least one current task.",
                   primary=dict(label="New task", key="new_task", tone="solid", icon=":material/add:")):
        task_dialog("")
    render_board(ws)
    if not ws.tasks_in("current"):
        import streamlit as st
        st.caption("Heads up: nothing is in Current. Move one task there to keep the project moving.")
