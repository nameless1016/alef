from services import chat_service, seed
from services.ai.llm_client import LLMCompletion
from services.assistant import AlefAssistant, LocalAssistant, is_live_ai


class FakeLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def complete(self, messages, max_tokens=None):
        self.calls.append(messages)
        nxt = self.responses.pop(0)
        if isinstance(nxt, Exception):
            raise nxt
        return nxt


def test_initial_mode_unlocks_project_on_project_init():
    ws = seed.default_workspace()
    chat_id = ws.chats[0].id
    llm = FakeLLM([
        LLMCompletion(
            content=(
                "Confirmed. Next step: start player controller.\n"
                "<project_init>\n"
                "<doc_update># Starlight\nCore loop.</doc_update>\n"
                "<map_update># Starlight\n## Gameplay\n- Move</map_update>\n"
                "<task_update>- [ ] Build player controller #core (due: 2026-12-01)</task_update>\n"
                "</project_init>"
            ),
            finish_reason="stop",
        )
    ])
    assistant = AlefAssistant(llm)
    assert is_live_ai(assistant) is True

    reply = chat_service.send_message(ws, assistant, chat_id, "Yes, initialize it.")
    assert reply is not None and not reply.is_error
    assert ws.is_initialized() is True
    assert ws.short_doc() is not None
    assert ws.primary_map() is not None
    assert len(ws.tasks) == 1
    assert ws.unsynced_count() == 0
    assert "<project_init>" not in ws.get_chat(chat_id).messages[-1].text
    # Ensure user message was sent exactly once (no duplication)
    user_msgs = [m for m in llm.calls[0] if m["role"] == "user" and m["content"] == "Yes, initialize it."]
    assert len(user_msgs) == 1


def test_change_sync_gate_marks_synced_on_success_and_keeps_unsynced_on_error():
    ws = seed.demo_workspace()
    ws.sync_context()
    ws.add_task("Add patrol cone debug draw", column="current")
    assert ws.unsynced_count() == 1

    failing = AlefAssistant(FakeLLM([RuntimeError("timeout")]))
    _, err_reply = chat_service.sync_with_alef(ws, failing)
    assert err_reply.is_error is True
    assert ws.unsynced_count() == 1

    working = AlefAssistant(
        FakeLLM([LLMCompletion(content="Noted the debug draw task. Next step: wire gizmos.", finish_reason="stop")])
    )
    chat_id, ok_reply = chat_service.sync_with_alef(ws, working)
    assert ok_reply.is_error is False
    assert ws.unsynced_count() == 0
    assert "debug draw" in ws.get_chat(chat_id).messages[-1].text.lower()


def test_normal_chat_auto_syncs_pending_changes_on_success():
    ws = seed.demo_workspace()
    ws.sync_context()
    ws.add_task("Verify camera FOV shader", column="current")
    assert ws.unsynced_count() == 1
    llm = FakeLLM([LLMCompletion(content="Acknowledged FOV shader task. Next step: benchmark.", finish_reason="stop")])
    reply = chat_service.send_message(ws, AlefAssistant(llm), ws.chats[0].id, "How does our scope look?")
    assert reply is not None and not reply.is_error
    assert "Verify camera FOV shader" in llm.calls[0][0]["content"]
    assert ws.unsynced_count() == 0


def test_recontextualize_updates_short_doc_without_modifying_long_doc():
    ws = seed.demo_workspace()
    gdd = next(d for d in ws.docs("doc") if d.role == "long")
    original_gdd = gdd.markdown
    llm = FakeLLM([
        LLMCompletion(
            content=(
                "Short doc refreshed from GDD. Next step: verify slice gate.\n"
                "<doc_update># Glasshouse Protocol\nUpdated concise brief.</doc_update>"
            ),
            finish_reason="stop",
        )
    ])
    reply = chat_service.recontextualize_doc(ws, AlefAssistant(llm), gdd.id)
    assert not reply.is_error
    assert gdd.markdown == original_gdd
    assert "Updated concise brief." in ws.short_doc().markdown


def test_truncated_reply_preserves_state_and_appends_notice():
    ws = seed.default_workspace()
    chat_id = ws.chats[0].id
    llm = FakeLLM([
        LLMCompletion(
            content="Setting up.\n<project_init><doc_update># Cut off",
            finish_reason="length",
        )
    ])
    reply = chat_service.send_message(ws, AlefAssistant(llm), chat_id, "Confirm")
    assert reply is not None
    assert ws.is_initialized() is False
    assert "500-token" in reply.text
    assert is_live_ai(LocalAssistant()) is False


def test_truncated_non_init_reply_applies_zero_partial_actions():
    ws = seed.demo_workspace()
    original_brief = ws.short_doc().markdown
    chat_id = ws.chats[0].id
    llm = FakeLLM([
        LLMCompletion(
            content=(
                "Trimming scope now.\n"
                "<doc_update># Glasshouse Protocol\nShould not be applied partially.</doc_update>\n"
                "<task_update>- [ ] Cut off mid task"
            ),
            finish_reason="length",
        )
    ])
    reply = chat_service.send_message(ws, AlefAssistant(llm), chat_id, "Trim scope")
    assert reply is not None
    assert reply.actions == []
    assert ws.short_doc().markdown == original_brief
    assert "500-token" in reply.text
