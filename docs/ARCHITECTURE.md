# ARCHITECTURE.md - 100Solutionz Lead Intelligence Platform

## Overview
Modular, production-ready B2B lead generation and AI outreach platform.

## Structure
- app/ - Streamlit UI (multi-page)
- config/ - YAML configs + Pydantic settings/schema
- core/ - Utils, DB, logging, exceptions, config loader
- database/ - SQLAlchemy models + repository (dedup)
- discovery/ - Apify-based discovery
- enrichment/ - Website analysis, extraction, tech detection
- intelligence/ - AI classification, opportunity detection, scoring, audit
- outreach/ - Email generation/validation, campaigns, sender, followups
- exports/ - Excel/CSV
- security/ - Suppression, secrets, compliance
- tests/ - Unit/integration/e2e
- scripts/, data/, docs/

## Key Principles
- Modular (no monolith)
- Multi-key deduplication (Place ID > domain > email > phone > name+addr)
- AI provider abstraction
- Evidence-based personalization (no fake claims/placeholders)
- Human approval before sending
- Safety: dry-run by default, limits, suppression, validation
- Configurable via YAML + env
- Testable with mocks

## Data Flow
DISCOVER (Apify) ? NORMALIZE ? DEDUP ? ENRICH (website) ? CLASSIFY ? OPPORTUNITIES ? SCORE ? GENERATE EMAIL ? VALIDATE ? REVIEW ? QUEUE ? SEND ? TRACK
