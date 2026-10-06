from typing import Dict, Any


class WebsiteAudit:
    def audit(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        website = lead_data.get('website') or ''
        return {
            "website": website,
            "https": website.startswith('https://') if website else False,
            "mobile_friendly": "not_checked",
            "has_title": "not_checked",
            "has_meta_desc": "not_checked",
            "has_structured_data": "not_checked",
            "has_cta": "not_checked",
            "has_contact": "not_checked",
            "has_booking": "not_checked",
            "page_speed": "not_checked",
            "ssl_enabled": website.startswith('https://') if website else False,
            "audit_summary": "Basic audit - detailed checks require crawling"
        }
