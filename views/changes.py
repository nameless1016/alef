"""Context checkpoint screen."""
import streamlit as st

from components.page_header import page_header
from services.formatting import rel_short
from utils.actions import update_alef
from utils.state import get_ws
from utils.ui import esc, html


def render() -> None:
    ws = get_ws()
    pending = ws.unsynced_count()
    page_header("CONTEXT CHECKPOINT", "Changes Alef should know",
                "Sync meaningful updates before asking for the next recommendation.",
                primary=dict(label="Update Alef", key="update_alef", tone="solid",
                             icon=":material/auto_awesome:", on_click=update_alef,
                             disabled=pending == 0))
    changes = ws.changes_view()
    if not changes:
        html('<div class="a-empty-box">Nothing has changed yet. Edit a task or document and it shows up here.</div>')
        return
    rows, first_unsynced = [], True
    for c in changes[:12]:
        if c.synced:
            state = "synced"
        elif first_unsynced:
            state, first_unsynced = "new", False
        else:
            state = "recent"
        rows.append(f"""
        <div class="a-change a-change-{state}">
          <i class="a-change-dot"></i>
          <div><b>{esc(c.title)}</b><p>{esc(c.text)}</p></div>
          <span>{esc(rel_short(c.ts))}</span>
        </div>
        """)
    html(f'<div class="a-changes">{"".join(rows)}</div>')
    if pending == 0:
        st.caption("Alef is up to date with your project.")
