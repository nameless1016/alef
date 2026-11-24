"""Interactive mind map rendered in an iframe (collapse on click + zoom)."""
import html
import json

import streamlit.components.v1 as components

from services.markmap_service import VIEW_H, VIEW_W, layout, parse_markdown

_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500&family=JetBrains+Mono:wght@400&display=swap');
html,body{margin:0;height:100%;background:#0f0e12;font-family:'DM Sans',system-ui,sans-serif;overflow:hidden}
#frame{position:relative;box-sizing:border-box;height:100vh;border:1px solid #26232a;background:#0f0e12}
#stage{position:absolute;inset:0;transform-origin:50% 50%;transition:transform .15s ease}
svg{width:100%;height:100%;display:block}
.edge{fill:none;stroke-width:1.6}
.node{cursor:pointer}
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
  <div id="hint">Select a node to collapse its branch</div>
</div>
<script>
const parent = __PARENTS__;
const collapsed = new Set();
const hidden = id => { let p = parent[id]; while (p) { if (collapsed.has(p)) return true; p = parent[p]; } return false; };
function refresh() {
  document.querySelectorAll('[data-id]').forEach(el => { el.style.display = hidden(el.dataset.id) ? 'none' : ''; });
  document.querySelectorAll('.node').forEach(g => g.classList.toggle('is-collapsed', collapsed.has(g.dataset.id)));
}
document.querySelectorAll('.node').forEach(g => g.addEventListener('click', () => {
  const id = g.dataset.id;
  if (!Object.values(parent).includes(id)) return;
  collapsed.has(id) ? collapsed.delete(id) : collapsed.add(id);
  refresh();
}));
let zoom = 100;
const apply = () => { document.getElementById('stage').style.transform = 'scale(' + zoom / 100 + ')'; document.getElementById('pct').textContent = zoom + '%'; };
document.getElementById('in').onclick = () => { zoom = Math.min(200, zoom + 10); apply(); };
document.getElementById('out').onclick = () => { zoom = Math.max(40, zoom - 10); apply(); };
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
                     .replace("__PARENTS__", json.dumps(parents)))
    components.html(page, height=height, scrolling=False)
