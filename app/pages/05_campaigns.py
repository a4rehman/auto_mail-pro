import sys
from pathlib import Path
import streamlit as st

# Add project root to sys.path
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.ui_utils import init_page, get_db
from database.repository import LeadRepository
from database.models import Lead
from core.config_loader import load_yaml
from outreach.campaign_manager import CampaignManager

init_page("Campaign Strategies & Mapping", "📢")

camp_mgr = CampaignManager()
campaigns = camp_mgr.campaigns

st.markdown("### Targeted 100Solutionz Campaign Profiles")
st.caption("Each campaign configures tailored service offerings, pain-point targeting, and value propositions based on industry dynamics.")

db = get_db()
all_leads = db.query(Lead).all()
db.close()

# Summary Metrics
c1, c2, c3 = st.columns(3)
c1.metric("Active Campaigns", len(campaigns))
c2.metric("Assigned Leads", sum(1 for l in all_leads if l.campaign))
c3.metric("Unassigned Leads", sum(1 for l in all_leads if not l.campaign))

st.write("")

# Auto-assign button
if sum(1 for l in all_leads if not l.campaign) > 0:
    if st.button("⚡ Auto-Assign All Unassigned Leads to Matching Campaigns", type="primary"):
        db = get_db()
        assigned_count = 0
        for l in db.query(Lead).filter(Lead.campaign.is_(None)).all():
            ind = (l.industry or l.business_category or "").lower()
            for c_key in campaigns.keys():
                if c_key in ind or ind in c_key:
                    l.campaign = c_key
                    assigned_count += 1
                    break
        db.commit()
        db.close()
        st.success(f"Successfully mapped {assigned_count} leads to campaigns!")
        st.rerun()

st.divider()

# Campaign Cards Grid
cols = st.columns(2)
for idx, (camp_key, camp_data) in enumerate(campaigns.items()):
    col = cols[idx % 2]
    with col:
        leads_in_camp = [l for l in all_leads if l.campaign == camp_key or camp_key in (l.industry or "").lower()]
        
        with st.container():
            st.markdown(f"""
            <div class="lead-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; color:#818CF8;">{camp_data.get('name', camp_key.title())}</h4>
                    <span class="system-pill pill-active">{len(leads_in_camp)} Leads</span>
                </div>
                <p style="margin: 8px 0 4px 0; font-size: 0.85rem; color:#9CA3AF;">Campaign Key: <code>{camp_key}</code></p>
                <div style="margin-top: 8px;">
                    <strong style="font-size: 0.85rem;">Targeted Services:</strong>
                </div>
            """, unsafe_allow_html=True)

            services = camp_data.get("services", [])
            serv_tags = "".join([f'<span class="tech-tag" style="background:rgba(16,185,129,0.15); color:#10B981; border-color:rgba(16,185,129,0.3);">{s}</span>' for s in services])
            st.markdown(serv_tags, unsafe_allow_html=True)

            if leads_in_camp:
                with st.expander(f"View {len(leads_in_camp)} Leads"):
                    for l_c in leads_in_camp[:5]:
                        st.markdown(f"- **{l_c.business_name}** ({l_c.city or 'N/A'}) — Score: `{l_c.lead_score or 'N/A'}`")
                    if len(leads_in_camp) > 5:
                        st.caption(f"...and {len(leads_in_camp) - 5} more.")

            st.markdown("</div>", unsafe_allow_html=True)
            st.write("")
