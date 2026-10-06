from typing import Dict, Any, List
from intelligence.ai_analyzer import AIAnalyzer


OPPORTUNITIES = [
    "Website Development", "Website Redesign", "E-commerce Development", "Shopify Development",
    "Mobile App Development", "AI Chatbot", "AI Receptionist", "WhatsApp Automation",
    "Appointment Automation", "CRM Automation", "Local SEO", "Google Business optimization",
    "Ads Management", "Social Media Management", "Custom AI Integration", "Business Automation"
]


class OpportunityDetector:
    def __init__(self, ai_analyzer: AIAnalyzer = None):
        self.ai_analyzer = ai_analyzer or AIAnalyzer()
    
    def detect(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        name = lead_data.get('business_name') or ''
        industry = lead_data.get('industry') or lead_data.get('business_category') or ''
        website = lead_data.get('website') or ''
        tech = lead_data.get('technology_stack') or []
        prompt = f"""Identify best 100Solutionz service opportunity for this business.
Return ONLY JSON with: primary_opportunity (string), secondary_opportunities (list of 2-3 strings), opportunity_reason (brief evidence-based reason).
Consider services: {', '.join(OPPORTUNITIES[:12])}

Business: {name}
Industry: {industry}
Website: {website}
Tech: {tech}
"""
        try:
            res = self.ai_analyzer.analyze(prompt)
            if not res.get('primary_opportunity'):
                res['primary_opportunity'] = 'Website Development'
            if not res.get('secondary_opportunities'):
                res['secondary_opportunities'] = ['Local SEO', 'Business Automation']
            return res
        except:
            return {
                "primary_opportunity": "Website Development",
                "secondary_opportunities": ["Local SEO", "Business Automation"],
                "opportunity_reason": "Generic fit for local business"
            }
