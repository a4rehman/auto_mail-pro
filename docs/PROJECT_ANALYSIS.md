# PROJECT ANALYSIS — 100Solutionz Lead Intelligence Platform

**Date:** 2026-10-19
**Scope:** full repository analysis, live-URL verification, every UI button, and every backend process path.

---

## 1. What the project is

A modular Streamlit + Python platform that runs the full cold-outreach pipeline:

```
DISCOVER → NORMALIZE → DEDUPLICATE → ENRICH → TECH DETECT → CLASSIFY
→ OPPORTUNITY → SCORE → AI EMAIL → VALIDATE → HUMAN APPROVAL
→ QUEUE → SEND (SMTP / dry-run) → TRACK → EXPORT
```

### Module inventory (58 Python files)

| Layer | Files | Responsibility |
|---|---|---|
| `app/` | `streamlit_app.py`, `ui_utils.py`, `pages/01..09` | UI, shared CSS, DB session, demo seeding |
| `config/` | `settings.py`, `schema.py`, `*.yaml` | Pydantic settings, industry/campaign/location config |
| `core/` | `database.py`, `utils.py`, `logging.py`, `exceptions.py`, `config_loader.py`, `mail_utils.py` | Engine/session, pure helpers, logging, errors |
| `database/` | `models.py`, `repository.py` | `Lead` ORM (60+ columns), multi-key dedup CRUD |
| `discovery/` | `apify_client.py`, `search_builder.py`, `discovery_service.py`, `location_manager.py` | Apify search + normalization + offline mock generator |
| `enrichment/` | `website_analyzer.py`, `email_extractor.py`, `social_extractor.py`, `technology_detector.py` | Live crawl, extraction, 17-signature tech fingerprint |
| `intelligence/` | `ai_analyzer.py`, `business_classifier.py`, `opportunity_detector.py`, `lead_scoring.py`, `website_audit.py` | AI provider abstraction, classification, opportunity, 0-100 score |
| `outreach/` | `email_generator.py`, `email_validator.py`, `campaign_manager.py`, `sender.py`, `followup.py` | Email drafting, validation, campaign mapping, SMTP |
| `exports/` | `excel_export.py`, `csv_export.py` | Multi-sheet Excel + CSV |
| `security/` | `suppression.py`, `secrets.py`, `compliance.py` | DNC/unsubscribe, secret access, sender identity |
| `tests/unit/` | 5 files | 17 unit tests |
| `scripts/` | verification harnesses | see §5 |

---

## 2. Backend process map (what each button actually does)

| # | Page | Button | Backend path |
|---|---|---|---|
| 1 | Home | 🌱 Load Sample B2B Leads | `ui_utils.seed_demo_leads` → `LeadRepository.create_or_update` ×5 |
| 2 | Discovery | 🚀 Start Discovery Search | `DiscoveryService.discover_leads` (Apify) **or** `generate_mock_leads` → `SearchBuilder.build_google_maps_search` |
| 3 | Discovery | 💾 Deduplicate & Save All | `LeadRepository.create_or_update` per row (place-id → domain → email → phone dedup) |
| 4 | Discovery | ➕ Save Prospect | `LeadRepository.create_or_update` (source=`manual_entry`) |
| 5 | Discovery | 🚀 Ingest & Deduplicate All Rows (CSV) | pandas parse → `create_or_update` per row |
| 6 | Leads | 🔍 Run Intelligence & Scoring | `asyncio.run(WebsiteAnalyzer.analyze)` → `OpportunityDetector.detect` → `LeadScorer.score` → commit |
| 7 | Leads | ✍️ Generate AI Email | `EmailGenerator.generate` → store draft, `approved=False` |
| 8 | Leads | 🗑️ Delete Lead | `LeadRepository.delete_lead` |
| 9 | Intelligence | 🚀 Run Live Audit | `WebsiteAnalyzer.analyze` → `BusinessClassifier.classify` → `OpportunityDetector.detect` → `LeadScorer.score` |
| 10 | Intelligence | 💾 Save as Verified Lead | `create_or_update` with full audit payload |
| 11 | Intelligence | ⚡ Run Full Pipeline for All Pending | loop over unscored leads → enrich + detect + score |
| 12 | Campaigns | ⚡ Auto-Assign All Unassigned | match `industry` ↔ `campaigns.yaml` keys → set `campaign` |
| 13 | Review | 🚀 Batch Approve All | set `approved=True`, `pipeline_status=APPROVED` |
| 14 | Review | ✅ Approve & Queue | persist edited subject/body + approve |
| 15 | Review | 🔄 Regenerate | `EmailGenerator.generate` |
| 16 | Review | ❌ Reject / Suppress | `approved=False`, `do_not_contact=True`, reason stored |
| 17 | Review | ↩️ Revoke Approval | `approved=False` |
| 18 | Queue | 🚀 Process & Dispatch All | `EmailSender.send` per lead (dry-run safe) → `email_status=sent`, `sent_at` |
| 19 | Queue | Add to Suppression | set DNC + reason + timestamp on matching emails |
| 20 | Settings | 💾 Save API Credentials | mutates `settings.*` (Apify/OpenAI/model/temp) |
| 21 | Settings | Test Apify / Test OpenAI | presence check / real `chat.completions` ping |
| 22 | Settings | 💾 Save Outreach Settings | mutates SMTP + dry-run + compliance identity |
| 23 | Settings | Load Curated Sample Leads / Delete All Leads | seed / `query.delete()` |

---

## 3. Live URL verification

| URL | Result |
|---|---|
| `ai-cold-outreach-system.streamlit.app` | **HTTP 200**, `/healthz` = `{"status":"ok"}`. App was **asleep**; woke on demand. Renders the **old salon-only** app. Shows a runtime error: `Error loading results: [Errno 2] No such file or directory: 'data'`. Broken logo 404 (`100solutionz.vercel.app/logo.png`). Console: 404/402 errors. |
| `automail-pro.streamlit.app` | **Redirects to `share.streamlit.io/app/automail-pro/`** → *"You do not have access to this app or it does not exist."* The deployment is **gone**. |

> ⚠️ **Root cause for the second one:** the new platform was force-pushed over the
> `a4rehman/auto_mail-pro` repository. Streamlit Cloud deploys from that repo's
> `main`, so the old `app.py` (and `requirements.txt` shape) no longer exists →
> the hosted app was removed/broken. Restore by pointing the deployment at a
> repo that still has the AutoMail entrypoint, or re-create it from this repo.

The first app is a **separate repository** (`a4rehman/ai-cold-outreach-system`) and was not touched; it is up but has a pre-existing `data/` directory bug.

---

## 4. Bugs found & fixed

### 4.1 `NameError: name 'Lead' is not defined` — **FIXED**
`app/pages/03_leads.py` used `Lead` (lines 191, 249) without importing it, so
**"🔍 Run Intelligence & Scoring"** and **"✍️ Generate AI Email"** crashed on every lead.

```
app/pages/03_leads.py:191 in <module>
NameError: name 'Lead' is not defined
```
Fix: added `from database.models import Lead`.

### 4.2 Settings UI never reached the AI provider — **FIXED**
`OpenAIProvider` read `os.getenv("OPENAI_API_KEY")` and hard-coded
`gpt-4o-mini`. The Settings page writes to `settings.*`, which is a different
source. Verified: key entered in the UI arrived as `<EMPTY>`, model stayed
`gpt-4o-mini` even when set to `gpt-4o`. Effect: **the whole AI pipeline silently
fell back to generic templates** even with a valid key.
Fix: `ai_analyzer.py` now resolves key/model/temperature lazily from
`settings` → env → constructor args (constructor wins), and rebuilds the client
when the key changes.

### 4.3 JSON mode was never enabled — **FIXED**
All four JSON-expecting callers passed no `response_schema`, so
`response_format` was `{"type": "text"}` while prompts demanded JSON-only. Any
prose/markdown wrapper broke `json.loads` → `{"raw": ...}` → fallback templates.

Verified before → after:

```
BusinessClassifier.classify  response_format={'type':'text'}      → {'type':'json_object'}
OpportunityDetector.detect   response_format={'type':'text'}      → {'type':'json_object'}
EmailGenerator.generate      response_format={'type':'text'}      → {'type':'json_object'}
EmailValidator.validate      response_format={'type':'text'}      → {'type':'json_object'}
```
Also made parsing tolerant of ``` fences and surrounding prose, and stopped the
retry decorator from burning ~6 s retrying an unconfigured-key error.

### 4.4 Minor / cosmetic
- 48 pyflakes **unused-import** warnings (no remaining undefined names).
- `16 × use_container_width` deprecation notices (removed after 2025-12-31).
- `lead_scoring.py`: `digital_weakness` and `commercial_potential` are
  **hard-coded constants (8)**, not derived from evidence — weakens the
  "transparent score" requirement.
- `06_review.py` calls `EmailValidator.validate` (an AI call) for *every*
  pending lead on *every* rerun — with a real key this is repeated paid API
  traffic on each interaction; should be memoised/cached.
- Old `data/` directory bug on the legacy deployed app (not this repo).

---

## 5. Verification evidence

Harnesses added under `scripts/`:

| Script | Purpose | Result |
|---|---|---|
| `apptest_pages.py` | render all 10 pages headlessly | **10/10 PASS** |
| `apptest_buttons.py` | click every button, assert no exception | **0 failures** |
| `apptest_flows.py` | discovery→save→dedup, live audit, batch enrich, seed/wipe | **8/8 PASS** |
| `verify_exports.py` | write CSV + XLSX, list sheets | CSV 1,248 B; XLSX 8,866 B; sheets `Leads, High Priority, Approved, Sent` |
| `static_check.py` | compile + pyflakes all files | 58/58 compile; 0 undefined names |
| `check_ai_backend.py` | prove provider wiring / JSON mode | before: 0/4; after: 4/4 |
| `inspect_db.py` | dump DB state | working |
| `check_live_urls.py` / `check_live_health.py` / `check_live_ws.py` / `dump_live_text.py` | live URL probing | see §3 |

Unit tests: **17 passed** (`pytest tests -q`), including 9 new AI-provider
regression tests.

Notable proven behaviours:
- **Deduplication works:** re-running discovery + save left the count unchanged (15 → 15).
- **Dry-run is default:** dispatch marked leads `sent` without SMTP transmission.
- **Suppression works:** `do_not_contact` excludes leads from the queue.
- **Excel export** produces 4 sheets; **CSV** produces clean CSV.

---

## 6. Remaining recommendations (not yet done)

1. **Restore the `automail-pro` deployment** (it was destroyed by the force-push) — highest priority.
2. Derive `digital_weakness` / `commercial_potential` from real signals (SSL, mobile, CTA, booking, pixels) instead of constants.
3. Cache the AI validator in the review loop (cost + latency).
4. Remove the 48 unused imports and migrate off `use_container_width`.
5. Persist Settings changes to `.env`/secrets rather than session-only mutation.
6. Split long-running enrichment/outreach into a background worker (Streamlit is not suited to long jobs).
7. Add SSRF guards (scheme/host allow-list, private-IP block) to `WebsiteAnalyzer`, and cap response size.
8. Serve `data/` properly or make the legacy app tolerant of a missing directory.
