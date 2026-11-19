"""Context checkpoint screen."""
from components.page_header import page_header
from services.data_service import CHANGES
from utils.ui import html


def render() -> None:
    page_header("CONTEXT CHECKPOINT", "Changes Alef should know",
                "Sync meaningful updates before asking for the next recommendation.",
                action="Update Alef", action_key="update_alef",
                icon=":material/auto_awesome:", tone="solid")
    rows = "".join(f"""
    <div class="a-change a-change-{c['state']}">
      <i class="a-change-dot"></i>
      <div><b>{c['title']}</b><p>{c['text']}</p></div>
      <span>{c['when']}</span>
    </div>
    """ for c in CHANGES)
    html(f'<div class="a-changes">{rows}</div>')
