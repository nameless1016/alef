"""Modal dialogs. Call these from the script body (inside `if st.button(...)`)."""
from datetime import date, timedelta

import streamlit as st

from services.formatting import parse_estimate
from services.models import COLUMN_LABELS, COLUMNS, PRIORITIES
from utils.actions import navigate
from utils.state import get_ws


@st.dialog("Task", width="large")
def task_dialog(task_id: str = "") -> None:
    ws = get_ws()
    task = ws.get_task(task_id) if task_id else None
    k = task_id or "new"

    title = st.text_input("Title", value=task.title if task else "", key=f"td_title_{k}",
                          placeholder="What needs to happen?")
    description = st.text_area("Notes", value=task.description if task else "",
                               key=f"td_desc_{k}", height=90)
    c1, c2, c3 = st.columns(3)
    with c1:
        column = st.selectbox("Status", [c for c, _ in COLUMNS],
                              index=[c for c, _ in COLUMNS].index(task.column) if task else 0,
                              format_func=COLUMN_LABELS.get, key=f"td_col_{k}")
    with c2:
        priority = st.selectbox("Priority", list(PRIORITIES),
                                index=PRIORITIES.index(task.priority) if task else 1,
                                format_func=str.title, key=f"td_prio_{k}")
    with c3:
        estimate = st.text_input("Estimate", value=task.estimate if task else "1h",
                                 key=f"td_est_{k}", help="Examples: 30m, 2h, 1d")
    d1, d2 = st.columns([1, 2], vertical_alignment="bottom")
    with d1:
        scheduled = st.toggle("Scheduled", value=bool(task and task.due), key=f"td_sch_{k}")
    with d2:
        due = st.date_input("Due date", disabled=not scheduled, key=f"td_due_{k}",
                            value=date.fromisoformat(task.due) if task and task.due
                            else date.today() + timedelta(days=7))
    tags = st.text_input("Tags", value=", ".join(task.tags) if task else "", key=f"td_tags_{k}",
                         placeholder="gameplay, ui", help="Comma separated")

    save, toggle, delete = st.columns([1, 1, 1])
    error = None
    if save.button("Save task" if task else "Create task", type="primary", key=f"td_save_{k}",
                   use_container_width=True):
        if not title.strip():
            error = "Give the task a title."
        elif parse_estimate(estimate) is None:
            error = "Estimate should look like 30m, 2h or 1d."
        else:
            fields = dict(title=title.strip(), description=description.strip(), column=column,
                          priority=priority, estimate=estimate.strip(),
                          due=due.isoformat() if scheduled else None,
                          tags=[t.strip().lstrip("#") for t in tags.split(",") if t.strip()])
            if task:
                ws.update_task(task.id, **fields)
            else:
                ws.add_task(**fields)
            st.rerun()
    if task:
        if toggle.button("Reopen" if task.done else "Mark complete", key=f"td_done_{k}",
                         use_container_width=True):
            ws.toggle_done(task.id)
            st.rerun()
        if delete.button("Delete", key=f"td_del_{k}", use_container_width=True):
            ws.delete_task(task.id)
            st.rerun()
    if error:
        st.error(error)


@st.dialog("New file")
def new_item_dialog(kind: str) -> None:
    label = "map" if kind == "map" else "document"
    name = st.text_input(f"Name your {label}", key=f"new_{kind}_name",
                         placeholder="Surveillance feedback" if kind == "map" else "Level notes")
    if st.button(f"Create {label}", type="primary", key=f"new_{kind}_go"):
        doc = get_ws().new_document(kind, name)
        navigate(doc.page)
        st.rerun()
