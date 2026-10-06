from typing import Dict, Any
from intelligence.ai_analyzer import AIAnalyzer


class EmailGenerator:
    def __init__(self, ai_analyzer: AIAnalyzer = None):
        self.ai_analyzer = ai_analyzer or AIAnalyzer()
    
    def generate(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        name = lead_data.get('business_name') or ''
        industry = lead_data.get('industry') or ''
        website = lead_data.get('website') or ''
        opp = lead_data.get('primary_opportunity') or 'Website Development'
        reason = lead_data.get('opportunity_reason') or ''
        
        prompt = f"""Write a personalized cold email for 100Solutionz outreach.
Rules:
- NO placeholders like [Name], [Business Name]. Use natural language.
- Keep under 120 words.
- Be specific based on evidence.
- Give clear CTA.
- Don't invent facts not provided.
- Avoid generic compliments.
Return ONLY JSON: {{\"subject\": \"...\", \"email\": \"...\"}}

Business: {name}
Industry: {industry}
Website: {website}
Recommended service: {opp}
Reason: {reason}
"""
        try:
            res = self.ai_analyzer.analyze(prompt)
            if not res.get('subject'):
                res['subject'] = f"Quick question about {opp.lower()}"
            if not res.get('email'):
                res['email'] = f"Hi,\n\nI noticed {name} could benefit from {opp}. We'd be happy to discuss how 100Solutionz can help improve your online presence and generate more leads.\n\nWould you be open to a quick 15-min chat next week?\n\nBest,\n100Solutionz"
            return res
        except Exception:
            return {
                "subject": f"Quick question about {opp.lower()}",
                "email": f"Hi,\n\nI noticed {name} could benefit from {opp}. We'd be happy to discuss how 100Solutionz can help.\n\nWould you be open to a quick chat?\n\nBest,\n100Solutionz"
            }
