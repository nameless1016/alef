/* Alef: keep the chat pinned to the newest message. Exposes window.__alefScrollChat(). */
(function () {
  const D = document;

  function scroller() {
    const body = D.querySelector('.a-chat-body');
    let el = body && body.parentElement;
    while (el && el !== D.body) {            // nearest scrollable ancestor of the transcript
      const oy = getComputedStyle(el).overflowY;
      if ((oy === 'auto' || oy === 'scroll') && el.scrollHeight > el.clientHeight) return el;
      el = el.parentElement;
    }
    return D.querySelector('[data-testid="stMain"]') || D.querySelector('section.main')
      || D.scrollingElement;
  }

  function toBottom() {
    const el = scroller();
    if (el) el.scrollTop = el.scrollHeight;
  }

  window.__alefScrollChat = function () {
    // Streamlit finishes laying out after the script ends, so re-pin a few times.
    let cancelled = false;
    const stop = () => { cancelled = true; };
    const el = scroller();
    ['wheel', 'touchstart', 'keydown'].forEach(ev => window.addEventListener(ev, stop, { once: true, passive: true }));
    [0, 60, 160, 350, 700].forEach(ms => setTimeout(() => { if (!cancelled) toBottom(); }, ms));
    requestAnimationFrame(() => { if (!cancelled) toBottom(); });
  };
})();
