from services import seed
from services.library import Library
from services.workspace import Workspace


def test_legacy_schema2_dict_loads_and_infers_initialized():
    raw = {
        "schema": 2,
        "project": {"name": "Legacy", "engine": "Godot 4.3"},
        "tasks": [{"title": "Proto", "column": "current"}],
        "chats": [],
        "documents": [{"title": "Project Brief", "kind": "doc", "markdown": "# Brief"}],
        "changes": [],
    }
    ws = Workspace.from_dict(raw)
    assert ws.is_initialized() is True
    assert ws.short_doc() is not None and ws.short_doc().title == "Project Brief"


def test_default_workspace_and_library_create_start_uninitialized_with_setup_chat():
    ws = seed.default_workspace()
    assert ws.is_initialized() is False
    assert len(ws.chats) == 1
    assert ws.chats[0].title == "Project setup"

    lib = Library.single(seed.demo_workspace())
    pid = lib.create("Lantern Run", "Stealth platformer", "Godot 4.3", "Alex")
    created = lib.workspaces[pid]
    assert created.is_initialized() is False
    assert len(created.chats) == 1


def test_long_doc_edit_does_not_create_unsynced_change_entry():
    ws = seed.demo_workspace()
    ws.sync_context()
    gdd = next(d for d in ws.docs("doc") if d.role == "long")
    ws.update_document(gdd.id, markdown="# Updated long doc\nLots of lore.")
    assert ws.unsynced_count() == 0


def test_manual_task_and_short_doc_edits_produce_concrete_change_log_text():
    ws = seed.demo_workspace()
    ws.sync_context()
    ws.add_task("Add patrol cone gizmos", column="current", due="2026-12-03")
    brief = ws.short_doc()
    assert brief is not None
    ws.update_document(brief.id, markdown="# Brief\nShorter updated brief.")
    log = ws.change_log_text()
    assert "Add patrol cone gizmos" in log
    assert "Project Brief" in log


def test_ai_actions_do_not_trigger_change_sync_gate():
    ws = seed.default_workspace()
    ws.apply_action(
        {
            "type": "init_project",
            "short_doc": "# Starlight\nCore loop summary.",
            "map_markdown": "# Starlight\n## Gameplay\n- Dash",
            "tasks": [
                {"status": "todo", "title": "Build player movement", "tags": ["core"], "due": "2026-12-01"}
            ],
        },
        source="ai",
    )
    assert ws.is_initialized() is True
    assert ws.short_doc() is not None and ws.short_doc().role == "short"
    assert ws.primary_map() is not None
    assert len(ws.tasks) == 1
    assert ws.unsynced_count() == 0


def test_upsert_tasks_merges_by_title_maps_columns_preserves_metadata_and_enforces_active_task():
    ws = seed.default_workspace()
    t = ws.add_task(
        "Lock camera rules",
        column="current",
        priority="high",
        estimate="2h",
        description="Acceptance criteria first",
        _log=False,
    )
    ws.apply_action(
        {
            "type": "upsert_tasks",
            "tasks": [
                {"status": "doing", "title": "lock camera rules", "tags": ["gameplay"], "due": "2026-12-02"},
                {"status": "todo", "title": "Prototype second district", "tags": ["blocked"], "due": None},
                {"status": "todo", "title": "Polish menu audio", "tags": ["backlog"], "due": None},
            ],
        },
        source="ai",
    )
    updated = ws.get_task(t.id)
    assert updated.column == "progress"
    assert updated.priority == "high"
    assert updated.estimate == "2h"
    assert updated.description == "Acceptance criteria first"
    assert updated.due == "2026-12-02"
    assert ws.find_task("Prototype second district").column == "blocked"
    assert ws.find_task("Polish menu audio").column == "backlog"
    assert ws.unsynced_count() == 0

    # Complete the only active task -> Active Task Rule promotes first open non-blocked task
    ws.apply_action(
        {
            "type": "upsert_tasks",
            "tasks": [{"status": "done", "title": "Lock camera rules", "tags": [], "due": None}],
        },
        source="ai",
    )
    assert ws.get_task(t.id).column == "done"
    assert len(ws.current_tasks()) >= 1
    assert ws.find_task("Polish menu audio").column == "current"
