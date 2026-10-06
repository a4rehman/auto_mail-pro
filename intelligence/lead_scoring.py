from typing import Dict, Any


class LeadScorer:
    def score(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        score = 0
        breakdown = {
            "website_opportunity": 0,
            "technology_opportunity": 0,
            "service_fit": 0,
            "business_activity": 0,
            "review_strength": 0,
            "contactability": 0,
            "digital_weakness": 0,
            "commercial_potential": 0
        }
        
        # Website opportunity (15)
        if lead_data.get('website'):
            breakdown["website_opportunity"] = 14
        else:
            breakdown["website_opportunity"] = 5
        
        # Technology opportunity (15)
        tech = lead_data.get('technology_stack') or []
        if tech:
            breakdown["technology_opportunity"] = 12
        else:
            breakdown["technology_opportunity"] = 8
        
        # Service fit (20) - based on opportunity detection
        if lead_data.get('primary_opportunity'):
            breakdown["service_fit"] = 18
        else:
            breakdown["service_fit"] = 10
        
        # Business activity (10)
        if lead_data.get('review_count') and lead_data['review_count'] > 10:
            breakdown["business_activity"] = 9
        elif lead_data.get('review_count'):
            breakdown["business_activity"] = 6
        else:
            breakdown["business_activity"] = 4
        
        # Review strength (10)
        rating = lead_data.get('rating') or 0
        if rating >= 4.5:
            breakdown["review_strength"] = 9
        elif rating >= 4.0:
            breakdown["review_strength"] = 7
        elif rating > 0:
            breakdown["review_strength"] = 5
        else:
            breakdown["review_strength"] = 3
        
        # Contactability (10)
        contactable = 0
        if lead_data.get('email'):
            contactable += 5
        if lead_data.get('phone'):
            contactable += 3
        if lead_data.get('website'):
            contactable += 2
        breakdown["contactability"] = min(contactable, 10)
        
        # Digital weakness (10) - opportunity exists if weak
        breakdown["digital_weakness"] = 8  # default assumption of opportunity
        
        # Commercial potential (10)
        breakdown["commercial_potential"] = 8
        
        score = sum(breakdown.values())
        return {"lead_score": score, "score_breakdown": breakdown, "outreach_confidence": score / 100.0}
