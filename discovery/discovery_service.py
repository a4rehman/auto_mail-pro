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
            return self._normalize_results(items, params.get("industry", ""))
        except Exception as e:
            raise DiscoveryError(f"Discovery failed: {str(e)}")
    
    def _normalize_results(self, items: List[Dict[str, Any]], default_industry: str = "") -> List[Dict[str, Any]]:
        normalized = []
        for item in items:
            cat = item.get("categoryName") or item.get("categories") or default_industry or ""
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
                "rating": float(item["rating"]) if item.get("rating") else None,
                "review_count": int(item.get("reviewCount") or item.get("reviewsCount") or 0) if (item.get("reviewCount") or item.get("reviewsCount")) else None,
                "hours": str(item.get("openingHours") or item.get("hours") or ""),
                "business_category": cat,
                "industry": default_industry or cat,
                "source": "apify",
            }
            normalized.append(lead)
        return normalized

    def generate_mock_leads(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate realistic simulated leads for offline testing or demonstrations."""
        import random
        industry = params.get("industry", "dental_clinic")
        city = params.get("city", "Austin")
        state = params.get("state", "TX")
        count = min(params.get("max_results", 10), 20)

        industry_display = industry.replace("_", " ").title()
        prefixes = ["Apex", "Prime", "Elite", "Summit", "Vanguard", "Pinnacle", "Harmony", "Beacon", "Radiant", "Metro", "Lone Star", "Capitol", "Nexus", "Prestige"]
        suffixes = ["Center", "Group", "Associates", "Solutions", "Studio", "Partners", "Care", "Hub", "Practice"]

        leads = []
        for i in range(count):
            p = prefixes[i % len(prefixes)]
            s = suffixes[(i * 3) % len(suffixes)]
            biz_name = f"{p} {industry_display} {s}"
            clean_name = "".join(c for c in p if c.isalnum()).lower()
            domain = f"{clean_name}{city.lower()}hub.com"
            rating = round(random.uniform(3.8, 4.9), 1)
            reviews = random.randint(15, 240)
            phone = f"+1 ({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"

            leads.append({
                "business_name": biz_name,
                "website": f"https://www.{domain}",
                "email": f"contact@{domain}",
                "phone": phone,
                "address": f"{random.randint(100, 9999)} Main Street",
                "city": city,
                "state": state,
                "postal_code": f"78{random.randint(701, 759)}",
                "country": params.get("country", "USA"),
                "google_place_id": f"ChIJ_{clean_name}_{city.lower()}_{i}",
                "google_maps_url": f"https://maps.google.com/?q={biz_name}+{city}",
                "rating": rating,
                "review_count": reviews,
                "hours": "Mon-Fri: 9AM - 5PM",
                "business_category": industry_display,
                "industry": industry,
                "source": "simulated_discovery",
            })
        return leads

