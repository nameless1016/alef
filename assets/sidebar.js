/* Alef: draggable / hideable sidebar. Runs in the parent page (injected by components/ui_scripts.py). */
(function () {
  const W = window, D = document, KEY = 'alef.sidebar';
  const DEFAULT = 233, MIN = 180, MAX = 520, SNAP_HIDE = 130;
  const root = D.documentElement;
  let width = DEFAULT, hidden = false, drag = null;

  try {
    const saved = JSON.parse(localStorage.getItem(KEY) || '{}');
    if (saved.width) width = Math.min(MAX, Math.max(MIN, saved.width));
    hidden = !!saved.hidden;
  } catch (e) {}

  const save = () => { try { localStorage.setItem(KEY, JSON.stringify({ width, hidden })); } catch (e) {} };

  function apply() {
    root.style.setProperty('--side-w', (hidden ? 0 : width) + 'px');
    root.setAttribute('data-alef-side', hidden ? 'hidden' : 'open');
    if (handle) {
      handle.style.left = (hidden ? 0 : width) + 'px';
      tab.setAttribute('aria-label', hidden ? 'Show sidebar' : 'Hide sidebar');
      tab.title = hidden ? 'Show sidebar (Ctrl+B)' : 'Hide sidebar (Ctrl+B)';
    }
  }

  // ---- DOM: a full-height drag strip with a small "grab tab" in the middle
  D.getElementById('alef-side-handle')?.remove();
  const handle = D.createElement('div');
  handle.id = 'alef-side-handle';
  handle.innerHTML = '<div class="alef-side-line"></div>' +
    '<button type="button" class="alef-side-tab"><i></i><i></i><i></i></button>';
  D.body.appendChild(handle);
  const tab = handle.querySelector('.alef-side-tab');

  function toggle() { hidden = !hidden; if (!hidden && width < MIN) width = DEFAULT; apply(); save(); }

  function onDown(e) {
    if (e.button !== undefined && e.button !== 0) return;
    drag = { x: e.clientX, startW: hidden ? 0 : width, moved: false, onTab: !!e.target.closest('.alef-side-tab') };
    handle.setPointerCapture?.(e.pointerId);
    e.preventDefault();
  }
  function onMove(e) {
    if (!drag) return;
    const dx = e.clientX - drag.x;
    if (!drag.moved && Math.abs(dx) < 4) return;
    if (!drag.moved) { drag.moved = true; root.classList.add('alef-side-dragging'); }
    const w = drag.startW + dx;
    if (w < SNAP_HIDE) { hidden = true; }
    else { hidden = false; width = Math.min(MAX, Math.max(MIN, w, 0)); }
    apply();
  }
  function onUp() {
    if (!drag) return;
    const wasClick = !drag.moved;
    drag = null;
    root.classList.remove('alef-side-dragging');
    if (wasClick) toggle(); else save();
  }
  function onKey(e) {
    if ((e.ctrlKey || e.metaKey) && !e.shiftKey && !e.altKey && e.key.toLowerCase() === 'b') {
      e.preventDefault(); toggle();
    }
  }
  function onDbl(e) {                       // double-click the strip: reset width
    if (e.target.closest('.alef-side-tab')) return;
    hidden = false; width = DEFAULT; apply(); save();
  }

  handle.addEventListener('pointerdown', onDown);
  handle.addEventListener('pointermove', onMove);
  handle.addEventListener('pointerup', onUp);
  handle.addEventListener('pointercancel', onUp);
  handle.addEventListener('dblclick', onDbl);
  D.addEventListener('keydown', onKey);
  W.addEventListener('resize', apply);

  W.__alefSidebar = {
    destroy() {
      handle.remove(); D.removeEventListener('keydown', onKey); W.removeEventListener('resize', apply);
      root.style.removeProperty('--side-w'); root.removeAttribute('data-alef-side');
    },
  };
  apply();
})();
