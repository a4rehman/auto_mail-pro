from typing import Dict, Any, List
from discovery.apify_client import ApifyClient
from discovery.search_builder import SearchBuilder
from core.exceptions import DiscoveryError


class DiscoveryService:
    def __init__(self, apify_client: ApifyClient = None, search_builder: SearchBuilder = None):
        self.apify_client = apify_client or ApifyClient()
        self.search_builder = search_builder or SearchBuilder()
    
    def discover_leads(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            input_data = self.search_builder.build_google_maps_search(params)
            items = self.apify_client.run_and_get_items(input_data)
            return self._normalize_results(items)
        except Exception as e:
            raise DiscoveryError(f"Discovery failed: {str(e)}")
    
    def _normalize_results(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized = []
        for item in items:
            lead = {
                "business_name": item.get("title") or item.get("name") or "",
                "website": item.get("website") or item.get("url") or "",
                "email": item.get("email") or "",
                "phone": item.get("phone") or item.get("mobilePhone") or "",
                "address": item.get("address") or item.get("street") or "",
                "city": item.get("city") or "",
                "state": item.get("state") or item.get("region") or "",
                "postal_code": item.get("postalCode") or item.get("zip") or "",
                "country": item.get("country") or "USA",
                "google_place_id": item.get("placeId") or item.get("id") or "",
                "google_maps_url": item.get("googleMapsUrl") or item.get("url") or "",
                "rating": item.get("rating") or None,
                "review_count": item.get("reviewCount") or item.get("reviewsCount") or None,
                "hours": item.get("openingHours") or item.get("hours") or "",
                "category": item.get("categoryName") or item.get("categories") or "",
                "source": "apify",
            }
            normalized.append(lead)
        return normalized
