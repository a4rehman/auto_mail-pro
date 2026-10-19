"""Verify exports write real CSV/Excel files with the required sheets."""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.database import init_db, SessionLocal
from database.repository import LeadRepository
from app.ui_utils import seed_demo_leads
from exports.csv_export import CSVExporter
from exports.excel_export import ExcelExporter

init_db()
db = SessionLocal()
repo = LeadRepository(db)

# Re-seed sample data (analysis earlier wiped the DB)
added = seed_demo_leads(db)
print(f"Seeded {added} sample leads")
leads = repo.list_leads(limit=1000)
print(f"Total leads now: {len(leads)}")

# Serialize to dicts
rows = []
for l in leads:
    rows.append({
        "business_name": l.business_name,
        "industry": l.industry,
        "city": l.city,
        "state": l.state,
        "email": l.email,
        "phone": l.phone,
        "website": l.website,
        "rating": l.rating,
        "review_count": l.review_count,
        "lead_score": l.lead_score,
        "primary_opportunity": l.primary_opportunity,
        "pipeline_status": l.pipeline_status,
        "approved": l.approved,
        "email_status": l.email_status,
    })

csv_path = CSVExporter().export(rows, "data/leads_export.csv")
print("CSV written :", csv_path, Path(csv_path).exists(), Path(csv_path).stat().st_size, "bytes")

xlsx_path = ExcelExporter().export(rows, "data/leads_export.xlsx")
print("XLSX written:", xlsx_path, Path(xlsx_path).exists(), Path(xlsx_path).stat().st_size, "bytes")

# Inspect sheets
import openpyxl
wb = openpyxl.load_workbook(xlsx_path)
print("Excel sheets:", wb.sheetnames)

db.close()
