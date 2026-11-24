"""App chrome: fixed top bar and bottom status bar."""
from services.formatting import rel_synced
from utils import icons
from utils.state import get_ws
from utils.ui import esc, html


def render_topbar() -> None:
    ws = get_ws()
    pending = ws.unsynced_count()
    dot = "a-dot a-dot-warn" if pending else "a-dot"
    html(f"""
    <div class="a-topbar">
      <div class="a-brand"><span class="a-brand-mark">{icons.logo(15)}</span><span>ALEF</span></div>
      <div class="a-topbar-right">
        <span class="a-sync"><i class="{dot}"></i>{rel_synced(ws.last_sync)}</span>
        <span class="a-avatar a-avatar-user">{esc(ws.project.user_name[:1].upper() or '?')}{esc(ws.project.user_name[1:2].upper())}</span>
      </div>
    </div>
    """)


def render_statusbar() -> None:
    p = get_ws().project
    html(f"""
    <div class="a-statusbar">
      <div class="a-status-left">
        <span class="a-status-item">{icons.branch(12)}{esc(p.branch)}</span>
        <span class="a-status-item"><i class="a-dot"></i>{esc(p.status)}</span>
      </div>
      <div class="a-status-right">
        <span>{esc(p.engine)}</span><span>{esc(p.format)}</span><span>{esc(p.version)}</span>
      </div>
    </div>
    """)
