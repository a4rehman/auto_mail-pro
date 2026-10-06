import re
from typing import List, Optional

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


def extract_emails(text: str) -> List[str]:
    if not text:
        return []
    emails = set(EMAIL_RE.findall(text))
    # Basic filtering
    filtered = []
    for e in emails:
        el = e.lower()
        if any(x in el for x in ['sentry', 'noreply', 'no-reply']):
            continue
        if el.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            continue
        filtered.append(el)
    return sorted(set(filtered))
