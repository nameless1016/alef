from services import seed
from utils.router import is_page_locked


def test_locked_pages_only_when_live_ai_and_uninitialized():
    ws = seed.default_workspace()
    assert is_page_locked("tasks", ws, live_ai=True) is True
    assert is_page_locked("doc:abc", ws, live_ai=True) is True
    assert is_page_locked("map:abc", ws, live_ai=True) is True
    assert is_page_locked("changes", ws, live_ai=True) is True
    assert is_page_locked("chat:" + ws.chats[0].id, ws, live_ai=True) is False
    assert is_page_locked("settings", ws, live_ai=True) is False
    assert is_page_locked("today", ws, live_ai=True) is False
    # Offline LocalAssistant never locks tabs
    assert is_page_locked("tasks", ws, live_ai=False) is False
    # Initialized project unlocks all tabs
    ws.project.initialized = True
    assert is_page_locked("tasks", ws, live_ai=True) is False


def test_recontextualize_action_does_not_report_success_or_navigate_when_no_actions(monkeypatch):
    from services.assistant import AssistantReply
    from utils import actions

    ws = seed.demo_workspace()
    gdd = next(d for d in ws.docs("doc") if d.role == "long")
    toasts = []
    navigated = []

    monkeypatch.setattr(actions, "get_ws", lambda: ws)
    monkeypatch.setattr(actions, "get_assistant_instance", lambda: object())
    monkeypatch.setattr(
        actions.chat_service,
        "recontextualize_doc",
        lambda _ws, _a, _doc_id: AssistantReply(text="No update emitted.", actions=[], is_error=False),
    )
    monkeypatch.setattr(actions.st, "toast", lambda msg: toasts.append(msg))
    monkeypatch.setattr(actions, "navigate", lambda page: navigated.append(page))

    actions.recontextualize_document(gdd.id)
    assert navigated == []
    assert toasts == ["No update emitted."]
