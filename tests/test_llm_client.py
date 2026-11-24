from types import SimpleNamespace

from services.ai.llm_client import LLMCompletion, LLMConfig, OpenAILLMClient, load_config


def test_load_config_returns_none_without_api_key():
    assert load_config(env={}) is None


def test_load_config_defaults_and_clamps_max_tokens():
    cfg = load_config(env={"ALEF_API_KEY": "sk-test", "ALEF_MAX_TOKENS": "999"})
    assert cfg is not None
    assert cfg.api_key == "sk-test"
    assert cfg.base_url == "https://aiki-labs.up.railway.app/api/v1"
    assert cfg.model == "gpt-6-luna"
    assert cfg.max_tokens == 500


def test_load_config_clamps_low_and_invalid_max_tokens():
    cfg_low = load_config(env={"ALEF_API_KEY": "sk-test", "ALEF_MAX_TOKENS": "0"})
    assert cfg_low is not None and cfg_low.max_tokens == 1
    cfg_bad = load_config(env={"ALEF_API_KEY": "sk-test", "ALEF_MAX_TOKENS": "abc"})
    assert cfg_bad is not None and cfg_bad.max_tokens == 500


def test_openai_client_passes_clamped_max_completion_tokens_and_handles_missing_usage():
    captured = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="ok"), finish_reason="stop")],
                usage=None,
            )

    fake_sdk = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))
    cfg = LLMConfig(
        api_key="sk-test",
        base_url="https://example.test/v1",
        model="gpt-6-luna",
        max_tokens=500,
        timeout_seconds=30.0,
    )
    client = OpenAILLMClient(cfg, client=fake_sdk)

    res = client.complete([{"role": "user", "content": "hi"}], max_tokens=800)
    assert captured["model"] == "gpt-6-luna"
    assert captured["max_completion_tokens"] == 500
    assert res == LLMCompletion(content="ok", finish_reason="stop", prompt_tokens=0, completion_tokens=0)


def test_openai_client_handles_empty_content_and_usage_fields():
    class FakeCompletions:
        def create(self, **kwargs):
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=None), finish_reason="length")],
                usage=SimpleNamespace(prompt_tokens=120, completion_tokens=500),
            )

    fake_sdk = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))
    cfg = LLMConfig(
        api_key="sk-test",
        base_url="https://example.test/v1",
        model="gpt-6-luna",
        max_tokens=500,
        timeout_seconds=30.0,
    )
    res = OpenAILLMClient(cfg, client=fake_sdk).complete([{"role": "user", "content": "hi"}])
    assert res == LLMCompletion(content="", finish_reason="length", prompt_tokens=120, completion_tokens=500)
