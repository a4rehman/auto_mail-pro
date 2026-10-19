"""Check the live deployed Streamlit URLs."""
import sys
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

URLS = [
    "https://ai-cold-outreach-system.streamlit.app/",
    "https://automail-pro.streamlit.app/",
]

for url in URLS:
    print("=" * 70)
    print("URL:", url)
    try:
        with httpx.Client(timeout=45, follow_redirects=True) as c:
            r = c.get(url)
            print("  final URL  :", r.url)
            print("  status     :", r.status_code)
            text = r.text
            print("  bytes      :", len(text))
            low = text.lower()
            for kw in ("100solutionz", "salon", "lead", "automail", "sleep", "wake",
                       "get this app back up", "streamlit"):
                if kw in low:
                    print(f"  contains   : {kw}")
    except Exception as exc:
        print("  ERROR:", type(exc).__name__, exc)
