"""Regression tests for AI provider wiring and JSON parsing."""
import os

import pytest

import intelligence.ai_analyzer as aa
from intelligence.ai_analyzer import OpenAIProvider, JSON_OBJECT
from config.settings import settings


class _FakeCompletions:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)

        class Msg:
            content = self.payload

        class Choice:
            message = Msg()

        class Resp:
            choices = [Choice()]

        return Resp()


def _make_provider(payload):
    prov = OpenAIProvider()
    fake = _FakeCompletions(payload)

    class FakeChat:
        completions = fake

    class FakeClient:
        def __init__(self, api_key=None, **kw):
            self.chat = FakeChat()

    prov._client = FakeClient(api_key="x")
    prov._client_key = prov.api_key or "x"
    return prov, fake


def test_api_key_resolved_from_settings(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-from-settings")
    assert OpenAIProvider().api_key == "sk-from-settings"


def test_env_fallback_when_settings_empty(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")
    assert OpenAIProvider().api_key == "sk-from-env"


def test_model_and_temperature_follow_settings(monkeypatch):
    monkeypatch.setattr(settings, "AI_MODEL", "gpt-4o")
    monkeypatch.setattr(settings, "AI_TEMPERATURE", 0.25)
    prov = OpenAIProvider()
    assert prov.model == "gpt-4o"
    assert prov.temperature == 0.25


def test_explicit_args_override_settings(monkeypatch):
    monkeypatch.setattr(settings, "AI_MODEL", "gpt-4o-mini")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-settings")
    prov = OpenAIProvider(api_key="sk-explicit", model="gpt-4.1")
    assert prov.api_key == "sk-explicit"
    assert prov.model == "gpt-4.1"


def test_missing_key_raises_without_retry(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from core.exceptions import AIError

    with pytest.raises(AIError):
        OpenAIProvider().analyze("hello")


def test_json_object_schema_enables_json_mode(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")
    prov, fake = _make_provider('{"subject": "Hi", "email": "Body"}')
    out = prov.analyze("prompt", response_schema=JSON_OBJECT)
    assert out == {"subject": "Hi", "email": "Body"}
    assert fake.calls[0]["response_format"] == {"type": "json_object"}


def test_plain_text_schema_omits_json_mode(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")
    prov, fake = _make_provider("not json at all")
    out = prov.analyze("prompt")
    assert "response_format" not in fake.calls[0]
    assert out == {"raw": "not json at all"}


def test_parser_salvages_markdown_fenced_json(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")
    prov, _ = _make_provider('Sure!\n```json\n{"industry": "dental_clinic"}\n```')
    out = prov.analyze("prompt", response_schema=JSON_OBJECT)
    assert out == {"industry": "dental_clinic"}


def test_parser_salvages_json_embedded_in_prose(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")
    prov, _ = _make_provider('Here you go: {"is_good": "YES"} hope that helps')
    out = prov.analyze("prompt", response_schema=JSON_OBJECT)
    assert out == {"is_good": "YES"}
