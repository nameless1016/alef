"""Three-panel stats strip on Today, computed from the workspace."""
from datetime import date

from services.workspace import Workspace
from utils.ui import esc, html


def render_stats(ws: Workspace) -> None:
    p, m, h = ws.project, ws.milestone(), ws.scope_health()
    if m["date"]:
        month, day = f"{m['date']:%b}".upper(), str(m["date"].day)
        meta = f"{m['days_left']} days left · {m['critical']} critical tasks"
    else:
        month, day, meta = "—", "—", f"{m['critical']} critical tasks"
    target = "No target date"
    if p.target:
        t = date.fromisoformat(p.target)
        target = f"Target · {t:%b} {t.day}"
    html(f"""
    <div class="a-stats">
      <div class="a-stat">
        <div class="a-eyebrow">PROJECT PROGRESS</div>
        <div class="a-progress">
          <div class="a-progress-num"><b>{ws.progress()}%</b><small>SLICE</small></div>
          <div class="a-progress-text">
            <h3>{esc(p.name)}</h3>
            <p>{esc(p.description)}</p>
            <span class="a-amber">{esc(target)}</span>
          </div>
        </div>
      </div>
      <div class="a-stat">
        <div class="a-eyebrow">SCOPE HEALTH</div>
        <div class="a-health a-health-{h['tone']}"><span class="a-diamond">◆</span>{esc(h['label'])}</div>
        <p class="a-muted">{esc(h['text'])}</p>
        <div class="a-budget">
          <div class="a-scope-row"><span>Budget used</span><b>{p.budget_used}%</b></div>
          <div class="a-bar"><i style="width:{p.budget_used}%"></i></div>
        </div>
      </div>
      <div class="a-stat">
        <div class="a-eyebrow">NEXT MILESTONE</div>
        <div class="a-month">{month}</div>
        <div class="a-day">{day}</div>
        <h3>{esc(m['title'])}</h3>
        <p class="a-dim">{esc(meta)}</p>
      </div>
    </div>
    """)
