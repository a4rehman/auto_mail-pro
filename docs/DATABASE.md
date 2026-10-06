# DATABASE.md

## Lead Model (key fields)
- lead_id, business_name, domain, email, phone, google_place_id
- industry, country, state, city, website
- technology_stack (JSON), score_breakdown (JSON), secondary_opportunities (JSON)
- lead_score, approved, email_status, pipeline_status
- timestamps, audit_trail (JSON)

## Deduplication
Priority: 1) google_place_id 2) normalized domain 3) normalized email 4) normalized phone 5) business_name+address (hash)

## Database
Default: SQLite (data/leads.db). Supports PostgreSQL/Supabase via DATABASE_URL.
