import re
from typing import List, Dict

TECH_PATTERNS = {
    'WordPress': [r'wp-content|wp-includes'],
    'Shopify': [r'shopify\.com|cdn\.shopify'],
    'WooCommerce': [r'woocommerce'],
    'Wix': [r'wix\.com|static\.wixstatic'],
    'Squarespace': [r'squarespace\.com'],
    'Webflow': [r'webflow\.com'],
    'Magento': [r'magento'],
    'BigCommerce': [r'bigcommerce'],
    'Next.js': [r'__NEXT_DATA__|next\.js'],
    'React': [r'react\.js|data-react'],
    'Laravel': [r'laravel'],
    'Google Analytics': [r'gtag|google-analytics\.com|ga\('],
    'Google Tag Manager': [r'googletagmanager\.com'],
    'Meta Pixel': [r'facebook\.com/tr|fbq\('],
    'HubSpot': [r'hubspot\.com'],
    'Intercom': [r'intercom\.io'],
    'Calendly': [r'calendly\.com'],
}


def detect_technologies(html: str, headers: Dict = None) -> List[Dict]:
    if not html:
        return []
    found = []
    for tech, pats in TECH_PATTERNS.items():
        for pat in pats:
            if re.search(pat, html, re.I):
                found.append({"technology_name": tech, "confidence": 0.8, "evidence": pat})
                break
    # Dedup by name
    seen = set()
    unique = []
    for f in found:
        if f['technology_name'] not in seen:
            seen.add(f['technology_name'])
            unique.append(f)
    return unique
