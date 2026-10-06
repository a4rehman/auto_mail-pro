# ARCHITECTURE_AUDIT.md - 100Solutionz Lead Intelligence Platform

**Date:** 2026-10-07  
**Location:** A:/ai-lead  
**Status:** Phase 1 - COMPLETE

## 1. EXECUTIVE SUMMARY

The workspace `A:/ai-lead` is a bare Git repo. Reference implementations were cloned to `A:/ai-lead-references/`:
- **ai-cold-outreach-system** - LangGraph-orchestrated Streamlit app for discovering beauty salons, scraping websites, AI analysis (GPT-4o-mini), email validation, and outreach.
- **auto_mail-pro** - Streamlit email automation reading from Google Sheets, personalizing templates with {{ColumnName}}, sending via SMTP.

The goal is a production-ready modular platform with Apify discovery, multi-industry support, website intelligence, technology/opportunity detection, lead scoring, human approval, compliance, deduplication, exports, database, etc.

## 2. EXISTING ARCHITECTURE

### 2.1 ai-cold-outreach-system
**Strengths:**
- Clean separation: src/lead_gen.py + src/outreach_core.py + streamlit_app.py
- LangGraph orchestration with WorkflowState (TypedDict + Annotated reducers)
- Nodes: discover_leads, scrape_website, analyze_with_ai, validate_with_ai, send_email, save_progress
- Pure utilities in outreach_core.py (clean_emails, website_root, validation, memory I/O)
- Progressive saving (JSON/CSV), processed memory for dedup
- AI email validation (checks placeholders/tone/length)
- Rich console + Streamlit UI, async-aware

**Weaknesses:**
- Hardcoded to beauty salons; fixed city list
- Discovery via Playwright + Google Local (brittle, rate-limited)
- No Apify, no configurable industries/locations
- No technology detection, business classification, opportunity detection, lead scoring
- No human approval, campaign YAML, Excel multi-sheet, DB layer, provider abstraction
- Headless=False in discovery (not prod), JSON as primary store

### 2.2 auto_mail-pro
**Strengths:**
- Clean: app.py + mail_utils.py, good Streamlit secrets handling
- Google Sheets API with service account, proper private key formatting
- {{ColumnName}} personalization, case-insensitive email lookup
- HTML emails, SMTP TLS, clear error feedback

**Weaknesses:**
- Google Sheets only (no DB/queue), no approval, no limits/throttling/retry
- No email validation, suppression, tracking, campaign mgmt
- oauth2client deprecated

## 3. KEY GAPS VS REQUIREMENTS
- Apify discovery (must build) - replace hardcoded Google search
- Comprehensive Lead model + DB (Postgres/Supabase) + dedup (multi-key)
- Website intelligence (multi-page, tech/social/extraction) + technology detector
- Business classifier + opportunity detector (map to 100Solutionz services) + lead scoring (0-100 breakdown)
- Human approval workflow, campaign system (YAML), compliance/suppression
- Excel multi-sheet export, modular architecture per spec, AI provider abstraction
- Concurrency controls, restartable pipeline state, expanded tests, security hardening

## 4. REUSABLE COMPONENTS
- outreach_core.py utilities (clean_emails, website_root, validation, memory I/O) - HIGHLY reusable
- LangGraph state/patterns, AI validation from lead_gen.py - partially reusable
- auto_mail-pro SMTP/Sheets patterns, personalize(), secrets handling - reusable

## 5. SECURITY/QUALITY CONCERNS
- Secrets management (.env/Streamlit secrets) - never commit; .env.example needed
- Untrusted scraped content (need sanitization, SSRF protections, timeouts, size limits)
- CSV/HTML injection risks; API key logging; Playwright deps for deployment
- Dedup insufficient (URL-only); need multi-key dedup + normalization

## 6. RECOMMENDED APPROACH
Adopt modular structure per master spec. Reuse refs. Replace brittle discovery with Apify. Build DB + full intelligence stack + approval + compliance. Keep refs for migration.

**Status:** Audit complete. Next: implementation plan + Phase 2-3 (structure/models/config).