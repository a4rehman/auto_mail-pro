# 100Solutionz Lead Intelligence Platform

A production-ready B2B lead-generation and AI outreach platform for identifying businesses with realistic commercial opportunities for 100Solutionz services.

## Overview

This platform automates the complete lead generation workflow: DISCOVER ? NORMALIZE ? DEDUPLICATE ? ENRICH ? ANALYZE ? SCORE ? PERSONALIZE ? REVIEW ? OUTREACH ? TRACK.

## Features

- **Apify-powered discovery** - Configurable search across countries, states, cities, industries
- **Website intelligence** - Automated analysis of business websites
- **AI-powered classification** - Business type and industry classification
- **Opportunity detection** - Identify best-fit 100Solutionz services
- **Lead scoring** - Transparent 0-100 scoring with breakdown
- **AI email generation** - Evidence-based personalized outreach
- **Human approval workflow** - Review before sending
- **Email validation & safety** - Suppression, limits, dry-run mode
- **Multi-format exports** - Excel (multi-sheet), CSV
- **Modular architecture** - Testable, maintainable, production-ready

## Quick Start

`ash
pip install -r requirements.txt
cp .env.example .env  # Configure your API keys
streamlit run app/streamlit_app.py
`

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/ARCHITECTURE_AUDIT.md](docs/ARCHITECTURE_AUDIT.md).

## Development

This project follows a phased implementation approach. See master prompt for full details.
