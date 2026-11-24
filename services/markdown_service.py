"""Tiny, safe Markdown -> HTML renderer for documents. Pure Python.

Supports headings, > quotes, - bullets, paragraphs, **bold**, *italic*, `code`.
All input is escaped first, so user text can never inject HTML.
"""
import html
import re


def _inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def to_html(md: str) -> str:
    out, para, quote, bullets = [], [], [], []

    def flush():
        if para:
            out.append(f"<p class='a-doc-p'>{_inline(' '.join(para))}</p>")
            para.clear()
        if quote:
            out.append("<blockquote>" + "".join(f"<p>{_inline(q)}</p>" for q in quote) + "</blockquote>")
            quote.clear()
        if bullets:
            out.append("<ul>" + "".join(f"<li>{_inline(b)}</li>" for b in bullets) + "</ul>")
            bullets.clear()

    for line in md.splitlines():
        s = line.strip()
        if not s:
            flush()
        elif s.startswith("#"):
            flush()
            level = len(s) - len(s.lstrip("#"))
            text = s[level:].strip()
            out.append(f"<h2 class='a-h{min(level, 3)}'>{_inline(text)}</h2>")
        elif s.startswith(">"):
            if para or bullets:
                flush()
            quote.append(s.lstrip("> ").strip())
        elif s.startswith(("- ", "* ")):
            if para or quote:
                flush()
            bullets.append(s[2:].strip())
        else:
            if quote or bullets:
                flush()
            para.append(s)
    flush()
    return "".join(out) or "<p class='a-doc-p a-dim'>This document is empty. Choose Edit to start writing.</p>"
