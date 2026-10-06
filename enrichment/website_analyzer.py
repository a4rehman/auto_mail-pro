import asyncio
from typing import Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup
from enrichment.email_extractor import extract_emails
from enrichment.social_extractor import extract_social_links
from enrichment.technology_detector import detect_technologies
from core.exceptions import EnrichmentError


class WebsiteAnalyzer:
    def __init__(self, timeout: int = 30, max_pages: int = 5, max_concurrent: int = 5):
        self.timeout = timeout
        self.max_pages = max_pages
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def analyze(self, website: str) -> Dict[str, Any]:
        if not website:
            raise EnrichmentError("No website provided")
        url = website if website.startswith(('http://', 'https://')) else f'https://{website}'
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, headers={'User-Agent': 'Mozilla/5.0'}) as client:
                resp = await client.get(url)
                html = resp.text
                soup = BeautifulSoup(html, 'html.parser')
        except Exception as e:
            raise EnrichmentError(f"Failed to fetch website: {e}")
        
        title = soup.title.string if soup.title else ""
        meta_desc = ""
        for tag in soup.find_all('meta'):
            if tag.get('name') == 'description':
                meta_desc = tag.get('content') or ''
                break
        
        # Extract text (truncated)
        text = soup.get_text(' ', strip=True)
        if len(text) > 5000:
            text = text[:5000]
        
        emails = extract_emails(text + html)
        social = extract_social_links(html)
        tech = detect_technologies(html)
        
        return {
            "website_status": "200" if 'resp' in locals() and resp.status_code < 400 else "error",
            "website_title": title[:500] if title else "",
            "website_description": meta_desc[:1000] if meta_desc else "",
            "website_text": text,
            "emails_found": emails,
            "social_links": social,
            "technology_stack": tech,
            "ssl_enabled": url.startswith('https://'),
            "ecommerce_detected": any(t['technology_name'] in ('Shopify', 'WooCommerce', 'Magento', 'BigCommerce') for t in tech),
            "ecommerce_platform": next((t['technology_name'] for t in tech if t['technology_name'] in ('Shopify', 'WooCommerce', 'Magento', 'BigCommerce')), None),
            "chatbot_detected": any('chat' in str(t).lower() for t in tech),
            "whatsapp_detected": 'whatsapp' in html.lower(),
            "analytics_detected": any(t['technology_name'] in ('Google Analytics', 'Google Tag Manager') for t in tech),
            "google_tag_manager": any(t['technology_name'] == 'Google Tag Manager' for t in tech),
            "meta_pixel": any(t['technology_name'] == 'Meta Pixel' for t in tech),
        }
