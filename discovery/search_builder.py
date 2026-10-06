from typing import Dict, Any, Optional
from urllib.parse import urlencode


class SearchBuilder:
    def __init__(self, actor_id: Optional[str] = None):
        self.actor_id = actor_id
    
    def build_google_maps_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build Apify actor input for Google Maps scraping.
        Actor ID should be configurable via env; this is a template.
        """
        input_data = {
            "searchQuery": self._build_query(params),
            "maxResults": params.get("max_results", 50),
            "proxyConfiguration": {"useApifyProxy": True}
        }
        # Add optional filters if supported by actor
        if params.get("min_rating"):
            input_data["minRating"] = params["min_rating"]
        if params.get("min_reviews"):
            input_data["minReviews"] = params["min_reviews"]
        return input_data
    
    def _build_query(self, params: Dict[str, Any]) -> str:
        parts = []
        industry = params.get("industry", "local business")
        keyword = params.get("keyword")
        if keyword:
            parts.append(keyword)
        else:
            parts.append(industry)
        
        location_parts = []
        if params.get("city"):
            location_parts.append(params["city"])
        if params.get("state"):
            location_parts.append(params["state"])
        if params.get("country"):
            location_parts.append(params["country"])
        if params.get("postal_code"):
            location_parts.append(params["postal_code"])
        if location_parts:
            parts.append("in " + " ".join(str(p) for p in location_parts))
        return " ".join(str(p) for p in parts)
