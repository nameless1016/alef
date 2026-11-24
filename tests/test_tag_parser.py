from services.ai.tag_parser import parse_response, to_actions


def test_parse_standalone_updates_strips_stray_xml_and_ignores_unknown_tags():
    raw = """Focus on camera rules first. Next step: lock FOV constants.
<hallucinated_tag>drop me</hallucinated_tag>
<doc_update>
# Brief
<b>Stealth</b> puzzle in Godot 4.3.
</doc_update>
<map_update>
# Game
## Systems
### Cameras
#### Cones
##### Too deep heading
</map_update>
<task_update>
- [/] Lock <i>camera</i> detection rules #gameplay #vertical-slice (due: 2026-12-01)
- [x] Shader benchmark #performance (due: 20261128)
</task_update>"""
    parsed = parse_response(raw, finish_reason="stop")
    assert parsed.reply_text == "Focus on camera rules first. Next step: lock FOV constants."
    assert "hallucinated_tag" in parsed.ignored_tags
    assert "<b>" not in parsed.doc_update and "Stealth" in parsed.doc_update
    assert "#####" not in parsed.map_update and "#### Too deep heading" in parsed.map_update
    assert len(parsed.task_updates) == 2
    assert parsed.task_updates[0].status == "doing"
    assert parsed.task_updates[0].title == "Lock camera detection rules"
    assert parsed.task_updates[0].tags == ["gameplay", "vertical-slice"]
    assert parsed.task_updates[0].due == "2026-12-01"
    assert parsed.task_updates[1].status == "done"
    assert parsed.task_updates[1].due == "2026-11-28"
    assert len(to_actions(parsed)) == 3


def test_parse_project_init_nested_tags():
    raw = """Project initialized. Next step: start the movement prototype.
<project_init>
<doc_update>
# Lantern Run
2D stealth platformer in Godot 4.3.
</doc_update>
<map_update>
# Lantern Run
## Gameplay Systems
- Movement
</map_update>
<task_update>
- [ ] Implement player movement #core-loop (due: 2026-12-05)
</task_update>
</project_init>"""
    parsed = parse_response(raw)
    assert parsed.project_init is not None
    assert "Lantern Run" in parsed.project_init.short_doc
    assert "# Lantern Run" in parsed.project_init.map_md
    assert len(parsed.project_init.tasks) == 1
    actions = to_actions(parsed)
    assert len(actions) == 1 and actions[0]["type"] == "init_project"


def test_parse_project_init_markdown_heading_fallback():
    raw = """Ready to begin.
<project_init>
## Short Summary
Compact summary here.
## Map
# Game
## Gameplay
## Tasks
- [ ] Build prototype #core
</project_init>"""
    parsed = parse_response(raw)
    assert parsed.project_init is not None
    assert "Compact summary here." in parsed.project_init.short_doc
    assert "# Game" in parsed.project_init.map_md
    assert parsed.project_init.tasks[0].title == "Build prototype"


def test_truncated_project_init_emits_zero_actions_even_if_nested_doc_closed():
    raw = """Starting setup now.
<project_init>
<doc_update>
# Lantern Run
Short doc finished.
</doc_update>
<map_update>
# Lantern Run
## Gameplay"""
    parsed = parse_response(raw, finish_reason="length")
    assert parsed.truncated is True
    assert parsed.project_init is None
    assert parsed.doc_update is None
    assert to_actions(parsed) == []
    assert parsed.reply_text == "Starting setup now."


def test_doc_update_over_300_words_adds_warning():
    long_summary = " ".join(["word"] * 320)
    raw = f"Updated summary.\n<doc_update>\n{long_summary}\n</doc_update>"
    parsed = parse_response(raw)
    assert parsed.doc_update is not None
    assert any("300" in w for w in parsed.warnings)


def test_plain_conversational_reply_without_tags():
    raw = "Keep the second district parked. Next step: write camera detection acceptance criteria."
    parsed = parse_response(raw)
    assert parsed.reply_text == raw
    assert parsed.truncated is False
    assert to_actions(parsed) == []


def test_invalid_calendar_due_dates_are_discarded_safely():
    raw = """Updated tasks.
<task_update>
- [ ] Fix collision mesh #physics (due: 2026-02-30)
- [ ] Build menu audio #audio (due: 20261301)
- [ ] Valid task #core (due: 2026-12-15)
</task_update>"""
    parsed = parse_response(raw)
    assert len(parsed.task_updates) == 3
    assert parsed.task_updates[0].due is None
    assert parsed.task_updates[1].due is None
    assert parsed.task_updates[2].due == "2026-12-15"
