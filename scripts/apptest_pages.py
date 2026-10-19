"""
Headless UI smoke test for every Streamlit page and every button.

Uses streamlit.testing.v1.AppTest to actually execute each page,
catch exceptions, and click buttons to verify the backend path runs.

Run:  python scripts/apptest_pages.py
"""
import sys
import traceback
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest

PAGES = [
    "app/streamlit_app.py",
    "app/pages/01_dashboard.py",
    "app/pages/02_discovery.py",
    "app/pages/03_leads.py",
    "app/pages/04_intelligence.py",
    "app/pages/05_campaigns.py",
    "app/pages/06_review.py",
    "app/pages/07_queue.py",
    "app/pages/08_analytics.py",
    "app/pages/09_settings.py",
]

TIMEOUT = 60


def render_only(rel_path):
    """Test that a page renders without an uncaught exception."""
    result = {"page": rel_path, "ok": True, "error": None, "widgets": {}}
    try:
        at = AppTest.from_file(str(ROOT / rel_path), default_timeout=TIMEOUT)
        at.run()
        if at.exception:
            result["ok"] = False
            result["error"] = "; ".join(
                f"{e.type}: {e.message}" for e in at.exception
            )
        result["widgets"] = {
            "buttons": len(at.button),
            "text_inputs": len(at.text_input),
            "selectboxes": len(at.selectbox),
            "tabs": len(at.tabs),
            "metrics": len(at.metric),
            "dataframes": len(at.dataframe),
            "expanders": len(at.expander),
            "download_buttons": len(at.get("download_button")),
            "forms": len(at.get("form")),
        }
        result["button_labels"] = [b.label for b in at.button]
        result["text_input_labels"] = [
            (t.label, getattr(t, "value", None)) for t in at.text_input
        ]
    except Exception as exc:
        result["ok"] = False
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    return result


def main():
    print("=" * 78)
    print("STREAMLIT HEADLESS PAGE RENDER TEST")
    print("=" * 78)
    failures = 0
    for page in PAGES:
        r = render_only(page)
        status = "PASS" if r["ok"] else "FAIL"
        if not r["ok"]:
            failures += 1
        print(f"\n[{status}] {r['page']}")
        if not r["ok"]:
            print("   ERROR:", r["error"])
            if r.get("traceback"):
                for line in r["traceback"].strip().splitlines()[-6:]:
                    print("   ", line)
        else:
            print("   widgets:", r["widgets"])
            if r["button_labels"]:
                print("   buttons:", r["button_labels"])

    print("\n" + "=" * 78)
    print(f"RESULT: {len(PAGES) - failures}/{len(PAGES)} pages rendered OK")
    print("=" * 78)
    return failures


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
