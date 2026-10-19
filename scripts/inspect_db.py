"""Inspect the local lead database state."""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import settings

db_path = settings.DATABASE_URL.replace("sqlite:///", "")
print("DATABASE_URL :", settings.DATABASE_URL)
print("resolved path:", db_path)
print("exists       :", Path(db_path).exists())

con = sqlite3.connect(db_path)
cur = con.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("tables       :", [r[0] for r in cur.fetchall()])

cur.execute("SELECT COUNT(*) FROM leads")
print("row count    :", cur.fetchone()[0])

cur.execute(
    "SELECT id, business_name, industry, pipeline_status, lead_score, "
    "email_status, approved, do_not_contact FROM leads ORDER BY id"
)
print("\nid | business_name | industry | status | score | email_status | approved | dnc")
for row in cur.fetchall():
    print(" | ".join(str(x) for x in row))

con.close()
