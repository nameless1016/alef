"""Strict post-processing parser for Alef's 4 whitelisted structured output tags."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional, Tuple

ALLOWED_TAGS = ("project_init", "doc_update", "map_update", "task_update")

_OPEN_ALLOWED_RE = re.compile(
    r"<\s*(project_init|doc_update|map_update|task_update)\b[^>]*>",
    re.IGNORECASE,
)
_BLOCK_TAG_RE = re.compile(
    r"<\s*([a-zA-Z_][a-zA-Z0-9_-]*)\b[^>]*>(.*?)</\s*\1\s*>",
    re.IGNORECASE | re.DOTALL,
)
_STRAY_TAG_RE = re.compile(r"</?\s*[a-zA-Z_][a-zA-Z0-9_-]*(?:\s+[^<>]*)?/?>")
_TRAILING_PARTIAL_TAG_RE = re.compile(r"<\s*/?\s*[a-zA-Z_][a-zA-Z0-9_-]*[^>]*$")

_TASK_LINE_RE = re.compile(r"^\s*[-*]\s*\[( |/|x|X)\]\s+(.+)$")
_DUE_RE = re.compile(r"\(\s*due\s*:\s*(\d{4}-\d{2}-\d{2}|\d{8})\s*\)", re.IGNORECASE)
_HASH_TAG_RE = re.compile(r"(?<!\w)#([a-zA-Z0-9][a-zA-Z0-9_-]*)")

_HEADING_OVER_4_RE = re.compile(r"^#{5,6}(\s+)", re.MULTILINE)
_SECTION_HEADING_RE = re.compile(r"^\s*#{1,4}\s+(.+?)\s*$")


@dataclass(frozen=True)
class ParsedTask:
    status: str               # "todo" | "doing" | "done"
    title: str
    tags: List[str] = field(default_factory=list)
    due: Optional[str] = None


@dataclass(frozen=True)
class ParsedInit:
    short_doc: Optional[str] = None
    map_md: Optional[str] = None
    tasks: List[ParsedTask] = field(default_factory=list)


@dataclass(frozen=True)
class ParsedResponse:
    reply_text: str
    project_init: Optional[ParsedInit] = None
    doc_update: Optional[str] = None
    map_update: Optional[str] = None
    task_updates: List[ParsedTask] = field(default_factory=list)
    truncated: bool = False
    ignored_tags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def _strip_xml_tags(text: str) -> str:
    """Remove any XML/HTML tags from extracted text while preserving Markdown line breaks."""
    cleaned = _STRAY_TAG_RE.sub("", text or "")
    lines = [re.sub(r"[ \t]{2,}", " ", line).rstrip() if not line.startswith((" ", "\t")) else line.rstrip()
             for line in cleaned.splitlines()]
    return "\n".join(lines).strip()


def _normalize_due(raw: str) -> Optional[str]:
    normalized = f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}" if len(raw) == 8 and raw.isdigit() else raw
    try:
        date.fromisoformat(normalized)
    except ValueError:
        return None
    return normalized


def _parse_task_lines(block: str) -> List[ParsedTask]:
    tasks: List[ParsedTask] = []
    for line in (block or "").splitlines():
        m = _TASK_LINE_RE.match(line)
        if not m:
            continue
        marker = m.group(1).lower()
        status = "done" if marker == "x" else ("doing" if marker == "/" else "todo")
        body = _STRAY_TAG_RE.sub("", m.group(2)).strip()

        due: Optional[str] = None
        dm = _DUE_RE.search(body)
        if dm:
            due = _normalize_due(dm.group(1))
            body = _DUE_RE.sub("", body)

        tags: List[str] = []
        for tm in _HASH_TAG_RE.finditer(body):
            tag = tm.group(1).lower()
            if tag not in tags:
                tags.append(tag)
        body = _HASH_TAG_RE.sub("", body)
        title = re.sub(r"\s+", " ", body).strip(" -–—:")
        if not title:
            continue
        tasks.append(ParsedTask(status=status, title=title, tags=tags, due=due))
    return tasks


def _clean_doc(block: str, warnings: List[str]) -> Optional[str]:
    text = _strip_xml_tags(block)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        return None
    words = len(re.findall(r"\S+", text))
    if words > 300:
        warnings.append(f"Short Document update is {words} words (target is under 300 words).")
    return text


def _clean_map(block: str) -> Optional[str]:
    text = _strip_xml_tags(block)
    text = _HEADING_OVER_4_RE.sub(r"####\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        return None
    if not re.search(r"^#{1,4}\s+\S", text, re.MULTILINE):
        return None
    return text


def _extract_named_block(text: str, tag: str) -> Tuple[Optional[str], str]:
    pattern = re.compile(rf"<\s*{tag}\b[^>]*>(.*?)</\s*{tag}\s*>", re.IGNORECASE | re.DOTALL)
    matches = list(pattern.finditer(text))
    if not matches:
        return None, text
    content = matches[-1].group(1)
    stripped = pattern.sub("", text)
    return content, stripped


def _find_first_unclosed_allowed_tag(text: str) -> Optional[int]:
    """Return the start index of the earliest allowed opening tag that lacks a closing tag."""
    for m in _OPEN_ALLOWED_RE.finditer(text):
        tag = m.group(1).lower()
        close_re = re.compile(rf"</\s*{tag}\s*>", re.IGNORECASE)
        if not close_re.search(text, m.end()):
            return m.start()
    return None


def _parse_init_fallback_sections(inner: str, warnings: List[str]) -> ParsedInit:
    """Fallback parser if the model used Markdown headings instead of nested tags in <project_init>."""
    buckets: Dict[str, List[str]] = {"doc": [], "map": [], "tasks": []}
    current: Optional[str] = None
    for line in inner.splitlines():
        hm = _SECTION_HEADING_RE.match(line)
        if hm:
            heading = hm.group(1).strip().lower()
            if any(k in heading for k in ("short", "summary", "brief", "doc")):
                current = "doc"
                continue
            if any(k in heading for k in ("map", "markmap", "structure")):
                current = "map"
                continue
            if "task" in heading:
                current = "tasks"
                continue
        if current:
            buckets[current].append(line)

    short_doc = _clean_doc("\n".join(buckets["doc"]), warnings)
    map_md = _clean_map("\n".join(buckets["map"]))
    tasks = _parse_task_lines("\n".join(buckets["tasks"]))
    return ParsedInit(short_doc=short_doc, map_md=map_md, tasks=tasks)


def _parse_project_init(inner: str, warnings: List[str]) -> Optional[ParsedInit]:
    doc_raw, rest = _extract_named_block(inner, "doc_update")
    map_raw, rest = _extract_named_block(rest, "map_update")
    tasks_raw, _ = _extract_named_block(rest, "task_update")

    if doc_raw is not None or map_raw is not None or tasks_raw is not None:
        parsed = ParsedInit(
            short_doc=_clean_doc(doc_raw, warnings) if doc_raw is not None else None,
            map_md=_clean_map(map_raw) if map_raw is not None else None,
            tasks=_parse_task_lines(tasks_raw) if tasks_raw is not None else [],
        )
    else:
        parsed = _parse_init_fallback_sections(inner, warnings)

    if not parsed.short_doc and not parsed.map_md and not parsed.tasks:
        return None
    return parsed


def parse_response(raw_text: str, finish_reason: str = "stop") -> ParsedResponse:
    """Separate conversational reply from valid trailing XML-like update tags."""
    text = (raw_text or "").strip()
    warnings: List[str] = []
    ignored_tags: List[str] = []
    truncated = False

    # 1. Detect unclosed allowed tags FIRST (so inner closed tags inside an unclosed
    #    <project_init> are never promoted to standalone partial mutations).
    unclosed_idx = _find_first_unclosed_allowed_tag(text)
    if unclosed_idx is not None:
        truncated = True
        text = text[:unclosed_idx].rstrip()
    elif finish_reason == "length":
        partial = _TRAILING_PARTIAL_TAG_RE.search(text)
        if partial:
            truncated = True
            text = text[:partial.start()].rstrip()
        elif not text:
            truncated = True

    # 2. Extract complete <project_init> block if present
    init_raw, remainder = _extract_named_block(text, "project_init")
    project_init = _parse_project_init(init_raw, warnings) if init_raw is not None else None

    # 3. Extract complete standalone update blocks
    doc_raw, remainder = _extract_named_block(remainder, "doc_update")
    map_raw, remainder = _extract_named_block(remainder, "map_update")
    task_raw, remainder = _extract_named_block(remainder, "task_update")

    doc_update = _clean_doc(doc_raw, warnings) if doc_raw is not None else None
    map_update = _clean_map(map_raw) if map_raw is not None else None
    task_updates = _parse_task_lines(task_raw) if task_raw is not None else []

    # 4. Strip unknown/hallucinated XML blocks and record their tag names
    def _drop_unknown(match: re.Match) -> str:
        name = match.group(1).lower()
        if name not in ALLOWED_TAGS and name not in ignored_tags:
            ignored_tags.append(name)
        return ""

    remainder = _BLOCK_TAG_RE.sub(_drop_unknown, remainder)
    # Strip any remaining stray opening/closing allowed tag tokens from prose
    remainder = re.sub(
        r"</?\s*(project_init|doc_update|map_update|task_update)\b[^>]*>",
        "",
        remainder,
        flags=re.IGNORECASE,
    )
    reply_text = re.sub(r"\n{3,}", "\n\n", remainder).strip()

    return ParsedResponse(
        reply_text=reply_text,
        project_init=project_init,
        doc_update=doc_update,
        map_update=map_update,
        task_updates=task_updates,
        truncated=truncated,
        ignored_tags=ignored_tags,
        warnings=warnings,
    )


def _task_to_dict(task: ParsedTask) -> dict:
    return {"status": task.status, "title": task.title, "tags": list(task.tags), "due": task.due}


def to_actions(parsed: ParsedResponse) -> List[dict]:
    """Translate a ParsedResponse into Workspace.apply_action() payloads."""
    actions: List[dict] = []
    if parsed.project_init is not None:
        actions.append(
            {
                "type": "init_project",
                "short_doc": parsed.project_init.short_doc,
                "map_markdown": parsed.project_init.map_md,
                "tasks": [_task_to_dict(t) for t in parsed.project_init.tasks],
            }
        )
        return actions

    if parsed.doc_update:
        actions.append({"type": "update_short_doc", "markdown": parsed.doc_update})
    if parsed.map_update:
        actions.append({"type": "update_map", "markdown": parsed.map_update})
    if parsed.task_updates:
        actions.append({"type": "upsert_tasks", "tasks": [_task_to_dict(t) for t in parsed.task_updates]})
    return actions
