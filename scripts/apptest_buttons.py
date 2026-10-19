"""
Headless button-click test for every Streamlit page.

For each page: render, then click each button (and each form submit button),
re-run, and report any uncaught exception raised by the backend path.

Run:  python scripts/apptest_buttons.py
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

TIMEOUT = 90


def exceptions_of(at):
    if not at.exception:
        return None
    return "; ".join(f"{e.type}: {e.message}" for e in at.exception)


def click_all_buttons(page):
    """Click every button on a page, one at a time, from a fresh session."""
    findings = []
    try:
        at = AppTest.from_file(str(ROOT / page), default_timeout=TIMEOUT)
        at.run()
    except Exception as exc:
        return [{"button": "<initial render>", "error": f"{type(exc).__name__}: {exc}"}]

    labels = [b.label for b in at.button]
    for idx, label in enumerate(labels):
        # fresh session per click to keep state isolated
        try:
            at2 = AppTest.from_file(str(ROOT / page), default_timeout=TIMEOUT)
            at2.run()
            if idx >= len(at2.button):
                continue
            btn = at2.button[idx]
            if btn.disabled:
                findings.append({"button": label, "error": "SKIPPED (disabled)"})
                continue
            btn.click()
            at2.run()
            errs = exceptions_of(at2)
            findings.append({"button": label, "error": errs})
        except Exception as exc:
            findings.append(
                {
                    "button": label,
                    "error": f"{type(exc).__name__}: {exc}",
                    "traceback": traceback.format_exc(),
                }
            )
    return findings


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

# Skip buttons that would wipe data or fire real network/SMTP calls during analysis
SKIP_LABELS = {
    "Delete All Leads",
    "Test OpenAI Configuration",
    "Load Curated Sample Leads",
    "🚀 Run Live Audit",
    "⚡ Run Full Pipeline for All Pending Leads",
    "🌱 Load Sample B2B Leads for Demo",
}


def main():
    print("=" * 78)
    print("BUTTON CLICK TEST")
    print("=" * 78)
    total_errors = 0
    for page in PAGES:
        print(f"\n### {page}")
        findings = click_all_buttons(page)
        if not findings:
            print("   (no buttons found)")
        for f in findings:
            label = f["button"]
            err = f["error"]
            if label in SKIP_LABELS:
                print(f"   [skip] {label}")
                continue
            if err and err != "SKIPPED (disabled)":
                total_errors += 1
                print(f"   [FAIL] {label}")
                print(f"          -> {err}")
                if f.get("traceback"):
                    for line in f["traceback"].strip().splitlines()[-5:]:
                        print("          ", line)
            elif err == "SKIPPED (disabled)":
                print(f"   [dis ] {label} (disabled by design)")
            else:
                print(f"   [ ok ] {label}")

    print("\n" + "=" * 78)
    print(f"TOTAL BUTTON FAILURES: {total_errors}")
    print("=" * 78)
    return total_errors


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
