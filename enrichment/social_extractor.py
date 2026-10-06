import re
from typing import List, Dict

SOCIAL_PATTERNS = {
    'facebook': r'facebook\.com/[^"\s]+',
    'instagram': r'instagram\.com/[^"\s]+',
    'linkedin': r'linkedin\.com/[^"\s]+',
    'twitter': r'twitter\.com/[^"\s]+|x\.com/[^"\s]+',
}


def extract_social_links(text: str) -> Dict[str, List[str]]:
    if not text:
        return {k: [] for k in SOCIAL_PATTERNS}
    results = {}
    for name, pat in SOCIAL_PATTERNS.items():
        results[name] = list(set(re.findall(pat, text, re.I)))
    return results
