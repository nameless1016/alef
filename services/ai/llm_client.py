"""Thin OpenAI-compatible LLM client wrapper and environment configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Mapping, Optional, Protocol

DEFAULT_BASE_URL = "https://aiki-labs.up.railway.app/api/v1"
DEFAULT_MODEL = "gpt-6-luna"
DEFAULT_MAX_TOKENS = 500
HARD_MAX_TOKENS = 500
DEFAULT_TIMEOUT_SECONDS = 45.0

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass(frozen=True)
class LLMCompletion:
    content: str
    finish_reason: str = "stop"
    prompt_tokens: int = 0
    completion_tokens: int = 0


@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    max_tokens: int = DEFAULT_MAX_TOKENS
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS


class LLMClient(Protocol):
    def complete(self, messages: List[dict], max_tokens: Optional[int] = None) -> LLMCompletion: ...


def _clamp_tokens(raw: Optional[str], fallback: int = DEFAULT_MAX_TOKENS) -> int:
    if raw is None or not str(raw).strip():
        return fallback
    try:
        value = int(str(raw).strip())
    except ValueError:
        return fallback
    return max(1, min(HARD_MAX_TOKENS, value))


def _parse_timeout(raw: Optional[str], fallback: float = DEFAULT_TIMEOUT_SECONDS) -> float:
    if raw is None or not str(raw).strip():
        return fallback
    try:
        value = float(str(raw).strip())
    except ValueError:
        return fallback
    return max(1.0, value)


def _read_streamlit_secrets() -> dict:
    try:
        import streamlit as st

        return dict(st.secrets)
    except Exception:
        return {}


def load_config(env: Optional[Mapping[str, str]] = None) -> Optional[LLMConfig]:
    """Load LLM configuration from env mapping, or .env + os.environ + st.secrets."""
    if env is None:
        try:
            from dotenv import load_dotenv

            load_dotenv(_REPO_ROOT / ".env", override=False)
        except Exception:
            pass
        merged: dict = _read_streamlit_secrets()
        merged.update(os.environ)
        source: Mapping[str, str] = merged
    else:
        source = env

    api_key = str(source.get("ALEF_API_KEY", "") or "").strip()
    if not api_key:
        return None

    base_url = str(source.get("ALEF_BASE_URL", "") or "").strip() or DEFAULT_BASE_URL
    model = str(source.get("ALEF_MODEL", "") or "").strip() or DEFAULT_MODEL
    max_tokens = _clamp_tokens(source.get("ALEF_MAX_TOKENS"))
    timeout_seconds = _parse_timeout(source.get("ALEF_TIMEOUT_SECONDS"))
    return LLMConfig(
        api_key=api_key,
        base_url=base_url,
        model=model,
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
    )


class OpenAILLMClient:
    """OpenAI SDK adapter targeting Alef's configured model and token budget."""

    def __init__(self, config: LLMConfig, client: Optional[Any] = None) -> None:
        self.config = config
        self._client = client

    def _get_client(self) -> Any:
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=self.config.timeout_seconds,
            )
        return self._client

    def complete(self, messages: List[dict], max_tokens: Optional[int] = None) -> LLMCompletion:
        budget = self.config.max_tokens if max_tokens is None else max_tokens
        clamped = max(1, min(HARD_MAX_TOKENS, int(budget)))
        response = self._get_client().chat.completions.create(
            model=self.config.model,
            messages=messages,
            max_completion_tokens=clamped,
        )
        choices = getattr(response, "choices", None) or []
        if not choices:
            return LLMCompletion(content="", finish_reason="stop")
        first = choices[0]
        message = getattr(first, "message", None)
        content = getattr(message, "content", None) or ""
        finish_reason = getattr(first, "finish_reason", None) or "stop"
        usage = getattr(response, "usage", None)
        prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0) if usage else 0
        completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0) if usage else 0
        return LLMCompletion(
            content=content,
            finish_reason=finish_reason,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
