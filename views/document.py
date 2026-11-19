"""Document screens."""
from components.page_header import page_header
from services.data_service import DOCUMENTS
from utils.ui import html


def _blocks_html(blocks: list) -> str:
    out = []
    for kind, content in blocks:
        if kind == "h1":
            out.append(f"<h2>{content}</h2>")
        elif kind == "quote":
            out.append("<blockquote>" + "".join(f"<p>{l}</p>" for l in content) + "</blockquote>")
        else:
            out.append(f"<p class='a-doc-p'>{content}</p>")
    return "".join(out)


def render(doc_key: str) -> None:
    doc = DOCUMENTS[doc_key]
    page_header(doc["eyebrow"].upper(), doc["title"], doc["subtitle"],
                action="Edit long version", action_key="edit_doc")
    gutter = "".join(f"<span>{i:02d}</span>" for i in range(1, doc["lines"] + 1))
    html(f"""
    <div class="a-doc">
      <div class="a-gutter">{gutter}</div>
      <div class="a-doc-content">{_blocks_html(doc['blocks'])}</div>
    </div>
    """)
