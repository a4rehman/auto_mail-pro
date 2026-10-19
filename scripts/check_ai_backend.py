"""
Diagnose the AI backend wiring:

  1. Does an API key entered via the Settings UI (settings.OPENAI_API_KEY)
     actually reach OpenAIProvider?  (It reads os.getenv instead.)
  2. Do the JSON-expecting callers enable OpenAI JSON mode
     (response_format={"type":"json_object"})?  (They don't pass a schema.)

We monkeypatch the OpenAI client so no network call happens.

Run:  python scripts/check_ai_backend.py
"""
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import settings
import intelligence.ai_analyzer as aa

CALLS = []


class FakeCompletions:
    def create(self, **kwargs):
        CALLS.append({k: v for k, v in kwargs.items() if k != "messages"})

        class Msg:
            content = '{"subject": "Hi", "email": "Body"}'

        class Choice:
            message = Msg()

        class Resp:
            choices = [Choice()]

        return Resp()


class FakeChat:
    completions = FakeCompletions()


class FakeClient:
    def __init__(self, api_key=None, **kw):
        self.api_key = api_key
        self.chat = FakeChat()

    def __getattr__(self, item):
        return FakeChat()


def patch_openai():
    import openai
    openai.OpenAI = FakeClient


patch_openai()

print("=" * 74)
print("1) SETTINGS -> PROVIDER WIRING")
print("=" * 74)
os.environ.pop("OPENAI_API_KEY", None)
settings.OPENAI_API_KEY = "sk-from-settings-ui"   # as the Settings page would set
settings.AI_MODEL = "gpt-4o"

prov = aa.OpenAIProvider()
print("os.environ['OPENAI_API_KEY'] :", os.environ.get("OPENAI_API_KEY"))
print("settings.OPENAI_API_KEY     :", settings.OPENAI_API_KEY)
print("provider.api_key            :", prov.api_key or "<EMPTY>")
print("provider.model              :", prov.model)
verdict1 = (prov.api_key == "sk-from-settings-ui")
print("--> key from Settings UI reaches provider?", verdict1)

print()
print("=" * 74)
print("2) JSON MODE / MODEL WIRING PER CALLER")
print("=" * 74)

from intelligence.business_classifier import BusinessClassifier
from intelligence.opportunity_detector import OpportunityDetector
from outreach.email_generator import EmailGenerator
from outreach.email_validator import EmailValidator

# give the provider a key via env so the calls actually execute
os.environ["OPENAI_API_KEY"] = "sk-env-test"
prov2 = aa.OpenAIProvider()

CALLS.clear()
BusinessClassifier(ai_analyzer=aa.AIAnalyzer(provider=prov2)).classify(
    {"business_name": "Acme Dental", "website": "https://acme.com"}
)
OpportunityDetector(ai_analyzer=aa.AIAnalyzer(provider=prov2)).detect(
    {"business_name": "Acme Dental", "industry": "dental_clinic"}
)
EmailGenerator(ai_analyzer=aa.AIAnalyzer(provider=prov2)).generate(
    {"business_name": "Acme Dental", "primary_opportunity": "AI Receptionist"}
)
EmailValidator(ai_analyzer=aa.AIAnalyzer(provider=prov2)).validate("Hi", "Body text")

names = ["BusinessClassifier.classify", "OpportunityDetector.detect",
         "EmailGenerator.generate", "EmailValidator.validate"]
json_mode_used = []
for name, call in zip(names, CALLS):
    rf = call.get("response_format")
    is_json = bool(rf and rf.get("type") == "json_object")
    json_mode_used.append(is_json)
    print(f"  {name:32s} response_format={rf}  model={call.get('model')}")

print()
print("--> all JSON-expecting callers enable JSON mode?", all(json_mode_used))
print(f"      ({sum(json_mode_used)}/{len(json_mode_used)} calls used json_object)")
