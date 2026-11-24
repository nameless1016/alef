"""Shared UI helpers: CSS loading, HTML rendering, escaping."""
import html as _html
from pathlib import Path

import streamlit as st

from services.models import ACCENTS

ROOT = Path(__file__).resolve().parent.parent
CSS_PATH = ROOT / "assets" / "styles.css"
LOGO_PATH = ROOT / "assets" / "logo.png"


def esc(text) -> str:
    """Escape user text for safe HTML embedding (newlines -> <br>)."""
    return _html.escape(str(text), quote=True).replace("\n", "<br>")


def compact(markup: str) -> str:
    """Strip indentation / blank lines so Markdown never treats HTML as code."""
    return "\n".join(line.strip() for line in markup.splitlines() if line.strip())


def html(markup: str) -> None:
    st.html(compact(markup))


def inject_css(content_width: int, badges: dict, accent: str = "Coral",
               full_bleed: bool = False) -> None:
    """Inject the stylesheet plus per-render dynamic rules in ONE element."""
    css = CSS_PATH.read_text(encoding="utf-8")
    main, ink = ACCENTS.get(accent, ACCENTS["Coral"])
    dynamic = [f":root{{--content-w:{content_width}px;--coral:{main};--coral-ink:{ink};}}"]
    if full_bleed:
        dynamic.append(
            '[data-testid="stMainBlockContainer"],.block-container'
            "{max-width:none !important;padding-left:0 !important;padding-right:0 !important;}")
    for key, count in badges.items():
        shown = "" if not count else str(count)
        dynamic.append(f'.st-key-nav_{key} button::after{{content:"{shown}";'
                       f'{"display:none;" if not count else ""}}}')
    st.markdown(f"<style>{css}\n{' '.join(dynamic)}</style>", unsafe_allow_html=True)
