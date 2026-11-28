"""Small browser-side behaviours (sidebar resize/hide, chat auto-scroll).

Streamlit has no hooks for these, so a zero-height component injects the script
into the parent page once. The scripts live in assets/ and are re-injected only
when their source changes.
"""
import hashlib
import json

from utils.ui import ROOT, embed_html

ASSETS = ROOT / "assets"

_LOADER = """
<script>
(function () {
  const doc = window.parent.document;
  const scripts = __SCRIPTS__;
  scripts.forEach(s => {
    const id = 'alef-script-' + s.name;
    const old = doc.getElementById(id);
    if (old && old.dataset.hash === s.hash) return;
    if (old) { old.remove(); const api = window.parent.__alefSidebar; if (s.name === 'sidebar' && api) api.destroy(); }
    const el = doc.createElement('script');
    el.id = id; el.dataset.hash = s.hash; el.textContent = s.src;
    doc.head.appendChild(el);
  });
})();
</script>
"""

_SCROLL = """
<script>
(function () {
  const p = window.parent;
  const token = __TOKEN__, chat = __CHAT__;
  const run = () => p.__alefScrollChat ? p.__alefScrollChat() : setTimeout(run, 50);
  p.__alefLastChat = chat;
  run();
})();
</script>
"""


def inject_scripts() -> None:
    """Load the sidebar + scroll helpers into the page (idempotent)."""
    payload = []
    for name in ("sidebar", "chat_scroll"):
        src = (ASSETS / f"{name}.js").read_text(encoding="utf-8")
        payload.append({"name": name, "src": src, "hash": hashlib.md5(src.encode()).hexdigest()[:10]})
    embed_html(_LOADER.replace("__SCRIPTS__", json.dumps(payload)))


def scroll_chat_to_bottom(chat_id: str, message_count: int) -> None:
    """Pin the transcript to the bottom. The token changes whenever a message is
    added or another chat is opened, which re-mounts the snippet and re-runs it."""
    token = f"{chat_id}:{message_count}"
    embed_html(_SCROLL.replace("__TOKEN__", json.dumps(token)).replace("__CHAT__", json.dumps(chat_id)))
