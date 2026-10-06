from typing import Dict, Any
from intelligence.ai_analyzer import AIAnalyzer


class BusinessClassifier:
    def __init__(self, ai_analyzer: AIAnalyzer = None):
        self.ai_analyzer = ai_analyzer or AIAnalyzer()
    
    def classify(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        website = lead_data.get('website') or ''
        name = lead_data.get('business_name') or ''
        desc = lead_data.get('website_description') or ''
        prompt = f"""Classify this business.
Return ONLY JSON with keys: industry (one of: dental_clinic, medical_clinic, private_healthcare, med_spa, hospital, beauty_salon, restaurant, ecommerce, fashion_store, real_estate, gym_fitness, hotel, auto_dealership, professional_services, local_business, other), business_type (local_service/retail/ecommerce/other), confidence (0-1).

Business: {name}
Website: {website}
Description: {desc}
"""
        try:
            res = self.ai_analyzer.analyze(prompt)
            return res
        except:
            return {"industry": "local_business", "business_type": "local_service", "confidence": 0.5}
