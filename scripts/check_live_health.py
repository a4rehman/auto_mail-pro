"""Probe Streamlit backend health endpoints for the live apps."""
import sys
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASES = [
    "https://ai-cold-outreach-system.streamlit.app",
    "https://automail-pro.streamlit.app",
]

PATHS = ["/_stcore/health", "/healthz", "/~/+/health", "/_stcore/host-config"]

for base in BASES:
    print("=" * 72)
    print("APP:", base)
    for p in PATHS:
        url = base + p
        try:
            with httpx.Client(timeout=30, follow_redirects=True) as c:
                r = c.get(url)
            body = r.text.strip()
            print(f"  {p:28s} -> {r.status_code} | {body[:200]!r}")
        except Exception as exc:
            print(f"  {p:28s} -> ERROR {type(exc).__name__}: {exc}")
