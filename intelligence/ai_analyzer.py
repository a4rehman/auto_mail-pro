import os
import json
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from core.exceptions import AIError


class AIProvider:
    def analyze(self, prompt: str, response_schema: Dict = None) -> Dict[str, Any]:
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini", temperature: float = 0.7):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self.temperature = temperature
        self._client = None
    
    def _get_client(self):
        if not self.api_key:
            raise AIError("OPENAI_API_KEY not configured")
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except Exception as e:
                raise AIError(f"Failed to init OpenAI: {e}")
        return self._client
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def analyze(self, prompt: str, response_schema: Dict = None) -> Dict[str, Any]:
        try:
            client = self._get_client()
            resp = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                response_format={"type": "json_object"} if response_schema else {"type": "text"}
            )
            content = resp.choices[0].message.content
            try:
                return json.loads(content)
            except:
                return {"raw": content}
        except Exception as e:
            raise AIError(f"AI analysis failed: {e}")


class AIAnalyzer:
    def __init__(self, provider: AIProvider = None):
        self.provider = provider or OpenAIProvider()
    
    def analyze(self, prompt: str, response_schema: Dict = None) -> Dict[str, Any]:
        return self.provider.analyze(prompt, response_schema)
