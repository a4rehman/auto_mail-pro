import os
import json
import re
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from core.exceptions import AIError
from config.settings import settings


# Schema sentinel used by callers that expect a JSON object back.
JSON_OBJECT = {"type": "json_object"}


class AIProvider:
    def analyze(self, prompt: str, response_schema: Dict = None) -> Dict[str, Any]:
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    """OpenAI-backed provider.

    Configuration is resolved lazily from (in priority order):
      1. explicit constructor arguments,
      2. the shared ``config.settings`` singleton (so the Settings page works
         at runtime without a restart),
      3. environment variables.
    """

    def __init__(self, api_key: str = None, model: str = None, temperature: float = None):
        self._api_key_override = api_key
        self._model_override = model
        self._temperature_override = temperature
        self._client = None
        self._client_key = None

    # --- lazily resolved configuration -----------------------------------
    @property
    def api_key(self) -> str:
        return (
            self._api_key_override
            or settings.OPENAI_API_KEY
            or os.getenv("OPENAI_API_KEY", "")
            or ""
        ).strip()

    @property
    def model(self) -> str:
        return self._model_override or settings.AI_MODEL or "gpt-4o-mini"

    @property
    def temperature(self) -> float:
        if self._temperature_override is not None:
            return self._temperature_override
        return settings.AI_TEMPERATURE

    def _get_client(self):
        """Create/reuse a client, rebuilding it if the active key changed."""
        key = self.api_key
        if not key:
            # Not retryable: configuration problem, fail fast.
            raise AIError("OPENAI_API_KEY not configured")
        if self._client is None or self._client_key != key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=key)
                self._client_key = key
            except Exception as e:  # pragma: no cover - import/init failure
                raise AIError(f"Failed to init OpenAI: {e}")
        return self._client

    @staticmethod
    def _parse_json(content: str) -> Dict[str, Any]:
        """Parse model output as JSON, tolerating markdown fences / prose."""
        if not content:
            return {"raw": ""}
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        # strip ```json ... ``` fences
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.S)
        if fenced:
            try:
                return json.loads(fenced.group(1))
            except json.JSONDecodeError:
                pass
        # first balanced-looking object
        brace = re.search(r"\{.*\}", content, re.S)
        if brace:
            try:
                return json.loads(brace.group(0))
            except json.JSONDecodeError:
                pass
        return {"raw": content}

    def analyze(self, prompt: str, response_schema: Dict = None) -> Dict[str, Any]:
        client = self._get_client()  # raises AIError fast when unconfigured
        return self._call(client, prompt, response_schema)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _call(self, client, prompt: str, response_schema: Dict = None) -> Dict[str, Any]:
        try:
            kwargs: Dict[str, Any] = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
            }
            if response_schema and response_schema.get("type") == "json_object":
                kwargs["response_format"] = {"type": "json_object"}
            resp = client.chat.completions.create(**kwargs)
            content = resp.choices[0].message.content or ""
            return self._parse_json(content)
        except AIError:
            raise
        except Exception as e:
            raise AIError(f"AI analysis failed: {e}")


class AIAnalyzer:
    def __init__(self, provider: AIProvider = None):
        self.provider = provider or OpenAIProvider()

    def analyze(self, prompt: str, response_schema: Dict = None) -> Dict[str, Any]:
        return self.provider.analyze(prompt, response_schema)
