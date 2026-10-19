"""Dump readable text from the live URLs to see whether the apps are awake."""
import sys
import re
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

URLS = [
    "https://ai-cold-outreach-system.streamlit.app/",
    "https://automail-pro.streamlit.app/",
]

for url in URLS:
    print("=" * 72)
    print("URL:", url)
    try:
        with httpx.Client(timeout=45, follow_redirects=True) as c:
            r = c.get(url)
        html = r.text
        # strip scripts/styles
        body = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
        body = re.sub(r"<style.*?</style>", " ", body, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", body)
        text = re.sub(r"\s+", " ", text).strip()
        print("status:", r.status_code, "| visible text length:", len(text))
        print("text  :", text[:800])
        # streamlit bootstrap markers
        for marker in ("stApp", "__STREAMLIT", "title>", "meta name=\"description\""):
            m = re.search(re.escape(marker) + r"[^>]{0,200}", html)
            if m:
                print(f"marker[{marker}]:", m.group(0)[:160])
        t = re.search(r"<title>(.*?)</title>", html, flags=re.S | re.I)
        print("title :", t.group(1).strip() if t else None)
    except Exception as exc:
        print("ERROR:", type(exc).__name__, exc)
