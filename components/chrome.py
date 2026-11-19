"""App chrome: fixed top bar and bottom status bar."""
from services.data_service import PROJECT
from utils import icons
from utils.ui import html


def render_topbar() -> None:
    html(f"""
    <div class="a-topbar">
      <div class="a-brand"><span class="a-brand-mark">{icons.logo(15)}</span><span>ALEF</span></div>
      <div class="a-topbar-right">
        <span class="a-sync"><i class="a-dot"></i>{PROJECT['synced']}</span>
        <span class="a-avatar a-avatar-user">{PROJECT['user_initials']}</span>
      </div>
    </div>
    """)


def render_statusbar() -> None:
    html(f"""
    <div class="a-statusbar">
      <div class="a-status-left">
        <span class="a-status-item">{icons.branch(12)}{PROJECT['branch']}</span>
        <span class="a-status-item"><i class="a-dot"></i>{PROJECT['status']}</span>
      </div>
      <div class="a-status-right">
        <span>{PROJECT['engine']}</span><span>{PROJECT['format']}</span><span>{PROJECT['version']}</span>
      </div>
    </div>
    """)
