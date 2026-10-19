"""
Multi-step flow test: discovery -> save -> intelligence -> approve -> dispatch,
plus the buttons skipped by the single-click harness.

Run:  python scripts/apptest_flows.py
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

TIMEOUT = 120
results = []


def click(at, label):
    """Click a button/widget by label. Returns True if found."""
    for b in at.button:
        if b.label == label:
            b.click()
            at.run()
            return True
    return False


def check(name, at, expect_no_exception=True):
    errs = None
    if at.exception:
        errs = "; ".join(f"{e.type}: {e.message}" for e in at.exception)
    ok = (errs is None) if expect_no_exception else True
    results.append((name, ok, errs))
    flag = "PASS" if ok else "FAIL"
    print(f"   [{flag}] {name}")
    if errs:
        print(f"          -> {errs}")
    return ok


def db_counts():
    import sqlite3
    from config.settings import settings
    p = settings.DATABASE_URL.replace("sqlite:///", "")
    con = sqlite3.connect(p)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM leads")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM leads WHERE pipeline_status='SENT'")
    sent = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM leads WHERE do_not_contact=1")
    dnc = cur.fetchone()[0]
    con.close()
    return total, sent, dnc


def flow_discovery():
    print("\n### FLOW: Discovery -> Deduplicate -> Save")
    at = AppTest.from_file(str(ROOT / "app/pages/02_discovery.py"), default_timeout=TIMEOUT)
    at.run()
    before = db_counts()[0]
    click(at, "🚀 Start Discovery Search")
    check("discovery search executes", at)
    try:
        discovered = at.session_state["discovered_leads"]
    except Exception:
        discovered = []
    n_found = len(discovered or [])
    print(f"          discovered {n_found} simulated prospects")
    ok = click(at, "💾 Deduplicate & Save All Discovered Leads to Database")
    check("save discovered leads to DB", at)
    after = db_counts()[0]
    print(f"          DB leads: {before} -> {after}")
    # Re-run the same discovery and save again -> dedup should add 0
    click(at, "🚀 Start Discovery Search")
    click(at, "💾 Deduplicate & Save All Discovered Leads to Database")
    after2 = db_counts()[0]
    results.append(("dedup prevents re-insert", after2 == after, None if after2 == after else f"{after} -> {after2}"))
    print(f"   [{'PASS' if after2==after else 'FAIL'}] dedup prevents duplicate re-insert ({after} -> {after2})")


def flow_intelligence_live_audit():
    print("\n### FLOW: Live URL Audit (network)")
    at = AppTest.from_file(str(ROOT / "app/pages/04_intelligence.py"), default_timeout=TIMEOUT)
    at.run()
    click(at, "🚀 Run Live Audit")
    check("live audit on https://www.example.com", at)
    if at.exception is None:
        try:
            res = at.session_state["live_audit_result"]
        except Exception:
            res = None
        if res:
            print(f"          status={res['audit'].get('website_status')} "
                  f"score={res['score'].get('lead_score')} "
                  f"opp={res['opportunity'].get('primary_opportunity')}")
            click(at, "💾 Save as Verified Lead in Database")
            check("save audited URL as lead", at)
        else:
            print("          (no result stored)")


def flow_batch_enrich():
    print("\n### FLOW: Batch Enrichment of Pending Leads")
    at = AppTest.from_file(str(ROOT / "app/pages/04_intelligence.py"), default_timeout=TIMEOUT)
    at.run()
    click(at, "⚡ Run Full Pipeline for All Pending Leads")
    check("batch enrich all pending leads", at)


def flow_sample_and_reset():
    print("\n### FLOW: Load Sample Leads / Delete All Leads")
    at = AppTest.from_file(str(ROOT / "app/pages/09_settings.py"), default_timeout=TIMEOUT)
    at.run()
    before = db_counts()[0]
    click(at, "Load Curated Sample Leads")
    check("load curated sample leads", at)
    mid = db_counts()[0]
    print(f"          DB leads: {before} -> {mid}")

    # tick the confirm checkbox then delete
    at2 = AppTest.from_file(str(ROOT / "app/pages/09_settings.py"), default_timeout=TIMEOUT)
    at2.run()
    for cb in at2.checkbox:
        cb.check()
    at2.run()
    if click(at2, "Delete All Leads"):
        check("delete all leads", at2)
        print(f"          DB leads after wipe: {db_counts()[0]}")


def flow_openai_test_button():
    print("\n### FLOW: Settings diagnostics button")
    at = AppTest.from_file(str(ROOT / "app/pages/09_settings.py"), default_timeout=TIMEOUT)
    at.run()
    click(at, "Test OpenAI Configuration")
    check("Test OpenAI Configuration (no key -> warning)", at)


def main():
    print("=" * 78)
    print("MULTI-STEP FLOW TEST")
    print("=" * 78)
    for fn in (
        flow_discovery,
        flow_intelligence_live_audit,
        flow_batch_enrich,
        flow_openai_test_button,
        flow_sample_and_reset,
    ):
        try:
            fn()
        except Exception as exc:
            results.append((fn.__name__, False, f"{type(exc).__name__}: {exc}"))
            print(f"   [FAIL] {fn.__name__} crashed: {exc}")
            traceback.print_exc()

    fails = [r for r in results if not r[1]]
    print("\n" + "=" * 78)
    print(f"FLOW CHECKS: {len(results) - len(fails)}/{len(results)} passed")
    for name, ok, err in fails:
        print(f"   FAILED: {name} -> {err}")
    print("=" * 78)
    return len(fails)


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
