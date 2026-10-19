import sys
from pathlib import Path
import streamlit as st

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.ui_utils import init_page, get_db, seed_demo_leads, render_score_badge
from database.repository import LeadRepository
from config.settings import settings

st.set_page_config(
    page_title="100Solutionz | Lead Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_page("100Solutionz Lead Intelligence Platform", "⚡", show_header=False)

# Hero Header
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(79, 70, 229, 0.15) 0%, rgba(99, 102, 241, 0.05) 100%);
            border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 16px; padding: 28px; margin-bottom: 24px;">
    <h1 style="margin: 0 0 8px 0; color: #FFFFFF; font-size: 2.2rem; font-weight: 700;">
        ⚡ 100Solutionz Lead Intelligence & Outreach
    </h1>
    <p style="margin: 0; color: #A5B4FC; font-size: 1.1rem; max-width: 800px;">
        AI-driven B2B lead generation, deep website tech audits, transparent 0-100 commercial scoring, 
        and evidence-based personalized cold outreach with human approval.
    </p>
</div>
""", unsafe_allow_html=True)

# Live Database Metrics
db = get_db()
repo = LeadRepository(db)
metrics = repo.get_metrics()
db.close()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Leads", metrics["total_leads"], help="All leads in local database")
col2.metric("High Score (≥80)", metrics["high_score"], help="Prime commercial opportunities")
col3.metric("Pending Review", metrics["pending_review"], help="AI emails waiting for human approval")
col4.metric("Ready in Queue", metrics["ready_outreach"], help="Approved leads ready to send")
col5.metric("Emails Dispatched", metrics["emails_sent"], help="Outreach sent (or dry-run logged)")

st.write("")

# Quick Seed Action if database is empty or small
if metrics["total_leads"] < 4:
    st.info("💡 **First-time setup detected**: Your database has minimal leads. Click below to load realistic B2B sample leads across Healthcare, Real Estate, E-commerce, and Fitness to explore the complete workflow immediately.")
    if st.button("🌱 Load Sample B2B Leads for Demo", type="primary", use_container_width=True):
        db = get_db()
        added = seed_demo_leads(db)
        db.close()
        st.success(f"Successfully loaded {added} rich sample leads with technology audits and email drafts!")
        st.rerun()

st.write("")

# Pipeline Workflow Grid
st.markdown("### 🔄 **End-to-End Platform Pipeline**")

pcol1, pcol2, pcol3 = st.columns(3)

with pcol1:
    st.markdown("""
    <div class="lead-card">
        <h4 style="margin-top:0; color: #818CF8;">1. Discovery & Ingestion</h4>
        <p style="font-size: 0.9rem; color: #D1D5DB;">
            Target prospects across countries, states, and industries using Google Maps scrapers or CSV bulk uploads with multi-key deduplication.
        </p>
        <p><a href="/discovery" target="_self">👉 Open Lead Discovery</a></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="lead-card">
        <h4 style="margin-top:0; color: #818CF8;">4. Campaign Strategies</h4>
        <p style="font-size: 0.9rem; color: #D1D5DB;">
            Align leads with tailored 100Solutionz service offerings (Web Redesign, AI Receptionist, WhatsApp Automation, Local SEO).
        </p>
        <p><a href="/campaigns" target="_self">👉 Open Campaigns</a></p>
    </div>
    """, unsafe_allow_html=True)

with pcol2:
    st.markdown("""
    <div class="lead-card">
        <h4 style="margin-top:0; color: #818CF8;">2. Website Tech Intelligence</h4>
        <p style="font-size: 0.9rem; color: #D1D5DB;">
            Live crawl targets to detect CMS, frameworks (Shopify, WordPress), Google Tag Manager, Meta Pixels, chatbots, and SSL.
        </p>
        <p><a href="/intelligence" target="_self">👉 Open Intelligence Audit</a></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="lead-card">
        <h4 style="margin-top:0; color: #818CF8;">5. Human Approval Workflow</h4>
        <p style="font-size: 0.9rem; color: #D1D5DB;">
            Review AI-crafted drafts with automated validation checks (no placeholders, under 120 words, CTA present) before approval.
        </p>
        <p><a href="/review" target="_self">👉 Open Email Review</a></p>
    </div>
    """, unsafe_allow_html=True)

with pcol3:
    st.markdown("""
    <div class="lead-card">
        <h4 style="margin-top:0; color: #818CF8;">3. AI Opportunity Scoring</h4>
        <p style="font-size: 0.9rem; color: #D1D5DB;">
            0-100 algorithmic score based on digital weaknesses, review health, contactability, and commercial fit.
        </p>
        <p><a href="/leads" target="_self">👉 Open Lead Database</a></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="lead-card">
        <h4 style="margin-top:0; color: #818CF8;">6. Safe Outreach Queue</h4>
        <p style="font-size: 0.9rem; color: #D1D5DB;">
            Send emails with safety throttling, dry-run simulation mode, CAN-SPAM compliance, and suppression list filtering.
        </p>
        <p><a href="/queue" target="_self">👉 Open Outreach Queue</a></p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Recent Activity Preview
st.markdown("### 📋 **Latest Leads in Platform**")
db = get_db()
repo = LeadRepository(db)
recent = repo.list_leads(limit=5)
db.close()

if recent:
    for lead in recent:
        with st.container():
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1.5])
            with c1:
                st.markdown(f"**{lead.business_name}**")
                st.caption(f"📍 {lead.city or 'Unknown City'}, {lead.state or ''} • 🌐 {lead.website or 'No Website'}")
            with c2:
                cat = lead.business_category or lead.industry or "General"
                st.markdown(f"*{cat}*")
                opp = lead.primary_opportunity or "Under Evaluation"
                st.caption(f"🎯 {opp}")
            with c3:
                badge = render_score_badge(lead.lead_score)
                st.markdown(badge, unsafe_allow_html=True)
                st.caption(f"Status: `{lead.pipeline_status or 'NEW'}`")
            with c4:
                if lead.approved:
                    st.success("✓ Approved")
                elif lead.generated_email:
                    st.warning("⏳ Needs Review")
                else:
                    st.info("Draft Pending")
else:
    st.info("No leads found yet. Use Lead Discovery or click 'Load Sample B2B Leads' above.")
