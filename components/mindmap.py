"""Interactive mind map rendered in an iframe (collapse on click + zoom)."""
import html
import json

import streamlit.components.v1 as components

from services.markmap_service import VIEW_H, VIEW_W, layout, parse_markdown

_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500&family=JetBrains+Mono:wght@400&display=swap');
html,body{margin:0;height:100%;background:#0f0e12;font-family:'DM Sans',system-ui,sans-serif;overflow:hidden}
#frame{cursor:grab;user-select:none;touch-action:none;overflow:hidden;position:relative;box-sizing:border-box;height:100vh;border:1px solid #26232a;background:#0f0e12}
#stage{position:absolute;inset:0}
svg{width:100%;height:100%;display:block}
.edge{fill:none;stroke-width:1.6}
.node{cursor:pointer}
#frame.grabbing{cursor:grabbing}
.node text{fill:#e9e6ec;font-size:11px;font-family:'DM Sans',system-ui,sans-serif}
.node .ul{stroke-width:1.2}
.node circle{fill:#0f0e12;stroke-width:1.6}
.node.is-collapsed circle{fill:currentColor}
#zoom{position:absolute;top:14px;right:14px;display:flex;border:1px solid #2c2930;background:#17151a;
  font:11px 'JetBrains Mono',monospace;color:#b9b5bf;z-index:2}
#zoom button{all:unset;cursor:pointer;width:26px;height:26px;text-align:center;line-height:26px}
#zoom button:hover{background:#221f26}
#zoom span{min-width:56px;text-align:center;line-height:26px;border-left:1px solid #2c2930;border-right:1px solid #2c2930}
#hint{position:absolute;right:14px;bottom:10px;font:9.5px 'JetBrains Mono',monospace;color:#5d5a63}
</style>
<div id="frame">
  <div id="zoom"><button id="out" aria-label="Zoom out">-</button><span id="pct">100%</span><button id="in" aria-label="Zoom in">+</button></div>
  <div id="stage">__SVG__</div>
  <div id="hint">Drag to pan · scroll to zoom · select a node to collapse</div>
</div>
<script>
const parent = __PARENTS__;
const collapsed = new Set();
const frame = document.getElementById('frame'), stage = document.getElementById('stage'), pct = document.getElementById('pct');
const MIN = 0.3, MAX = 12;
const VW = __VW__, VH = __VH__;
const svg = stage.querySelector('svg');
let view = { cx: VW / 2, cy: VH / 2, s: 1 };       // centre in SVG units, zoom relative to "fit"

const hidden = id => { let p = parent[id]; while (p) { if (collapsed.has(p)) return true; p = parent[p]; } return false; };
function refresh() {
  document.querySelectorAll('[data-id]').forEach(el => { el.style.display = hidden(el.dataset.id) ? 'none' : ''; });
  document.querySelectorAll('.node').forEach(g => g.classList.toggle('is-collapsed', collapsed.has(g.dataset.id)));
}
function metrics() {                                   // pixels per SVG unit at the current zoom
  const r = frame.getBoundingClientRect();
  return { fw: r.width, fh: r.height, k: Math.min(r.width / VW, r.height / VH) * view.s };
}
function apply() {                                     // re-render the vectors via viewBox: never blurry
  const { fw, fh, k } = metrics(), w = fw / k, h = fh / k;
  svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
  svg.setAttribute('viewBox', (view.cx - w / 2) + ' ' + (view.cy - h / 2) + ' ' + w + ' ' + h);
  pct.textContent = Math.round(view.s * 100) + '%';
}
function zoomAt(mx, my, factor) {                      // keep the point under (mx,my) fixed
  const m = metrics(), s2 = Math.min(MAX, Math.max(MIN, view.s * factor));
  const px = view.cx + (mx - m.fw / 2) / m.k, py = view.cy + (my - m.fh / 2) / m.k;
  view.s = s2;
  const k2 = metrics().k;
  view.cx = px - (mx - m.fw / 2) / k2;
  view.cy = py - (my - m.fh / 2) / k2;
  apply();
}
function zoomCentre(f) { const r = frame.getBoundingClientRect(); zoomAt(r.width / 2, r.height / 2, f); }

frame.addEventListener('wheel', e => {                 // scroll to zoom
  e.preventDefault();
  const r = frame.getBoundingClientRect();
  zoomAt(e.clientX - r.left, e.clientY - r.top, Math.exp(-e.deltaY * 0.0015));
}, { passive: false });

let drag = null;                                       // drag to pan, click to collapse
frame.addEventListener('pointerdown', e => {
  if (e.target.closest('#zoom') || e.button !== 0) return;
  drag = { x: e.clientX, y: e.clientY, moved: false };
  frame.classList.add('grabbing');
});
window.addEventListener('pointermove', e => {
  if (!drag) return;
  const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
  if (!drag.moved && Math.hypot(dx, dy) < 4) return;
  drag.moved = true; drag.x = e.clientX; drag.y = e.clientY;
  const k = metrics().k; view.cx -= dx / k; view.cy -= dy / k; apply();
});
window.addEventListener('pointerup', e => {
  if (!drag) return;
  const wasClick = !drag.moved;
  drag = null; frame.classList.remove('grabbing');
  const node = wasClick && e.target.closest ? e.target.closest('.node') : null;
  if (node && Object.values(parent).includes(node.dataset.id)) {
    const id = node.dataset.id;
    collapsed.has(id) ? collapsed.delete(id) : collapsed.add(id);
    refresh();
  }
});
frame.addEventListener('dblclick', () => { view = { cx: VW / 2, cy: VH / 2, s: 1 }; apply(); });
document.getElementById('in').onclick = () => zoomCentre(1.2);
document.getElementById('out').onclick = () => zoomCentre(1 / 1.2);
window.addEventListener('resize', apply);
apply();
</script>
"""


_EMPTY = """<body style="margin:0;height:100vh;box-sizing:border-box;border:1px solid #26232a;background:#0f0e12;
display:flex;align-items:center;justify-content:center;font:12px 'DM Sans',system-ui,sans-serif;color:#8c8892">
Add a # heading in the markdown to start this map.</body>"""


def _svg(nodes: list) -> str:
    edges, groups = [], []
    for n in nodes:
        if n["parent"] is not None:
            p = next(x for x in nodes if x["id"] == n["parent"])
            mx = (p["x"] + n["x"]) / 2
            edges.append(
                f'<path class="edge" data-id="{n["id"]}" stroke="{n["color"]}" '
                f'd="M{p["x"]:.1f} {p["y"]:.1f} C{mx:.1f} {p["y"]:.1f} {mx:.1f} {n["y"]:.1f} '
                f'{n["x"]:.1f} {n["y"]:.1f}"/>'
            )
    for n in nodes:
        x, y, w, c = n["x"], n["y"], n["text_w"], n["color"]
        is_root = n["depth"] == 0
        x1, x2 = (x - w, x) if is_root else (x, x + w)
        tx = x1 + 4
        r = 5.5 if is_root else 4
        groups.append(
            f'<g class="node" data-id="{n["id"]}" style="color:{c}">'
            f'<line class="ul" x1="{x1:.1f}" x2="{x2:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{c}"/>'
            f'<text x="{tx:.1f}" y="{y - 5:.1f}">{html.escape(n["label"])}</text>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" stroke="{c}"/></g>'
        )
    return (f'<svg viewBox="0 0 {VIEW_W} {VIEW_H}" preserveAspectRatio="xMidYMid meet" '
            f'xmlns="http://www.w3.org/2000/svg">{"".join(edges)}{"".join(groups)}</svg>')


def render_mindmap(markdown: str, height: int = 562) -> None:
    nodes = layout(parse_markdown(markdown))
    if not nodes:
        components.html(_EMPTY, height=height)
        return
    parents = {n["id"]: n["parent"] for n in nodes}
    page = (_TEMPLATE.replace("__SVG__", _svg(nodes))
                     .replace("__PARENTS__", json.dumps(parents))
                     .replace("__VW__", str(VIEW_W)).replace("__VH__", str(VIEW_H)))
    components.html(page, height=height, scrolling=False)
