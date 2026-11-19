"""Task board screen."""
from components.page_header import page_header
from components.task_card import board_html
from services.data_service import SPRINT
from utils.ui import html


def render() -> None:
    page_header(f"{SPRINT['label'].upper()} / {SPRINT['days_left']} DAYS LEFT",
                "Task board", "Every active project keeps at least one current task.",
                action="New task", action_key="new_task", icon=":material/add:", tone="solid")
    html(board_html())
