from typing import Dict, Any
from intelligence.ai_analyzer import AIAnalyzer, JSON_OBJECT


class EmailValidator:
    def __init__(self, ai_analyzer: AIAnalyzer = None):
        self.ai_analyzer = ai_analyzer or AIAnalyzer()
    
    def validate(self, subject: str, email_body: str) -> Dict[str, Any]:
        prompt = f"""Check this cold email. Return ONLY JSON:
{{"is_good": "YES" or "NO", "mistakes": ["..."], "improved_subject": "...", "improved_message": "..." }}

Rules:
- NO placeholders like [Name] or [Business Name]
- Keep under 120 words
- Natural and human
- Clear CTA
- No false claims

Subject: {subject}
Body: {email_body}
"""
        try:
            res = self.ai_analyzer.analyze(prompt, response_schema=JSON_OBJECT)
            return res
        except:
            return {"is_good": "YES", "mistakes": [], "improved_subject": subject, "improved_message": email_body}
