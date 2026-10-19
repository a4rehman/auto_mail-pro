import sys
from pathlib import Path
import asyncio
import pandas as pd
import streamlit as st

# Add project root to sys.path
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.ui_utils import init_page, get_db, render_score_badge
from database.models import Lead
from database.repository import LeadRepository
from enrichment.website_analyzer import WebsiteAnalyzer
from intelligence.opportunity_detector import OpportunityDetector
from intelligence.lead_scoring import LeadScorer
from outreach.email_generator import EmailGenerator
from exports.excel_export import ExcelExporter
from exports.csv_export import CSVExporter

init_page("Lead Intelligence Database", "👥")

db = get_db()
repo = LeadRepository(db)
all_leads = repo.list_leads(limit=1000)
db.close()

if not all_leads:
    st.info("No leads found in the database. Head over to Lead Discovery or the Dashboard to load prospects.")
    st.stop()

# Top Filters
f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1.5, 1.5, 1])
with f_col1:
    search = st.text_input("🔍 Search Leads", placeholder="Search by name, website, or email...")
with f_col2:
    industries = ["All"] + sorted(list(set(l.industry or "General" for l in all_leads)))
    sel_industry = st.selectbox("Industry", industries)
with f_col3:
    statuses = ["All", "DISCOVERED", "ANALYZED", "APPROVED", "SENT"]
    sel_status = st.selectbox("Pipeline Status", statuses)
with f_col4:
    min_score = st.slider("Min Score", 0, 100, 0, step=5)

# Filter logic
filtered = []
for l in all_leads:
    if search:
        s_low = search.lower()
        if (s_low not in (l.business_name or "").lower() and
            s_low not in (l.website or "").lower() and
            s_low not in (l.email or "").lower() and
            s_low not in (l.city or "").lower()):
            continue
    if sel_industry != "All" and (l.industry or "General") != sel_industry:
        continue
    if sel_status != "All" and (l.pipeline_status or "DISCOVERED") != sel_status:
        continue
    if (l.lead_score or 0) < min_score:
        continue
    filtered.append(l)

# Header summary & Export actions
st.write(f"Showing **{len(filtered)}** of **{len(all_leads)}** total prospects.")

exp_col1, exp_col2, _ = st.columns([1.5, 1.5, 3])
with exp_col1:
    # CSV Export
    csv_leads = [
        {
            "id": l.id,
            "business_name": l.business_name,
            "industry": l.industry,
            "city": l.city,
            "state": l.state,
            "phone": l.phone,
            "email": l.email,
            "website": l.website,
            "rating": l.rating,
            "review_count": l.review_count,
            "lead_score": l.lead_score,
            "primary_opportunity": l.primary_opportunity,
            "pipeline_status": l.pipeline_status,
            "approved": l.approved,
            "email_status": l.email_status
        }
        for l in filtered
    ]
    df_exp = pd.DataFrame(csv_leads)
    csv_bytes = df_exp.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Export CSV",
        data=csv_bytes,
        file_name="leads_export.csv",
        mime="text/csv",
        use_container_width=True
    )

with exp_col2:
    try:
        import io
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_exp.to_excel(writer, sheet_name='Leads', index=False)
            if 'lead_score' in df_exp.columns:
                high = df_exp[df_exp['lead_score'] >= 80]
                high.to_excel(writer, sheet_name='High Priority', index=False)
            if 'approved' in df_exp.columns:
                approved = df_exp[df_exp['approved'] == True]
                approved.to_excel(writer, sheet_name='Approved', index=False)
        st.download_button(
            "📊 Export Multi-Sheet Excel",
            data=excel_buffer.getvalue(),
            file_name="leads_intelligence_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except Exception as e:
        st.caption(f"Excel export unavailable: {e}")

st.write("")

# Display Leads List
for lead in filtered:
    with st.expander(f"🏢 **{lead.business_name}** — Score: {lead.lead_score or 'N/A'} | Status: {lead.pipeline_status or 'NEW'}", expanded=False):
        c1, c2, c3 = st.columns([1.5, 1.5, 1])

        with c1:
            st.markdown("##### 📍 Business Information")
            st.markdown(f"**Industry:** `{(lead.business_category or lead.industry or 'N/A')}`")
            st.markdown(f"**Location:** {lead.city or 'N/A'}, {lead.state or ''} ({lead.country or 'USA'})")
            st.markdown(f"**Address:** {lead.address or 'N/A'}")
            st.markdown(f"**Phone:** `{lead.phone or 'N/A'}`")
            st.markdown(f"**Email:** `{lead.email or 'N/A'}`")
            if lead.website:
                st.markdown(f"**Website:** [{lead.website}]({lead.website})")
            if lead.rating:
                st.markdown(f"**Google Reviews:** ⭐ {lead.rating} ({lead.review_count or 0} reviews)")

        with c2:
            st.markdown("##### 🔬 Website & Tech Intelligence")
            st.markdown(f"**SSL Active:** {'✅ Yes' if lead.ssl_enabled else '❌ No / Unchecked'}")
            st.markdown(f"**E-commerce:** {'🛍️ ' + str(lead.ecommerce_platform or 'Yes') if lead.ecommerce_detected else 'None'}")
            st.markdown(f"**Chatbot / WhatsApp:** {'🤖 Detected' if lead.chatbot_detected or lead.whatsapp_detected else '❌ None detected'}")
            
            tech_list = lead.technology_stack or []
            if tech_list:
                st.markdown("**Detected Tech:**")
                chips_html = "".join([f'<span class="tech-tag">{t.get("technology_name", "Tech")}</span>' for t in tech_list])
                st.markdown(chips_html, unsafe_allow_html=True)
            else:
                st.caption("No tech stack detected yet.")

            st.write("")
            st.markdown("##### 💡 Identified Opportunity")
            if lead.primary_opportunity:
                st.info(f"**{lead.primary_opportunity}**\n\n_{lead.opportunity_reason or 'Direct match for local business service.'}_")
            else:
                st.caption("Intelligence analysis not yet run.")

        with c3:
            st.markdown("##### 🎯 Lead Score")
            score_badge = render_score_badge(lead.lead_score)
            st.markdown(score_badge, unsafe_allow_html=True)

            if lead.score_breakdown:
                st.write("")
                with st.popover("📊 Score Details"):
                    for k, v in lead.score_breakdown.items():
                        st.write(f"**{k.replace('_', ' ').title()}:** {v} pts")

            st.write("")
            st.markdown("##### ✉️ Outreach Email")
            if lead.generated_email:
                if lead.approved:
                    st.success("✅ Email Approved")
                else:
                    st.warning("⏳ Pending Human Review")
            else:
                st.caption("Email not yet generated.")

        st.divider()

        # Action Buttons for this lead
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)

        with btn_col1:
            if st.button("🔍 Run Intelligence & Scoring", key=f"intel_{lead.id}", use_container_width=True):
                with st.spinner("Analyzing website and scoring..."):
                    db = get_db()
                    l_inst = db.query(Lead).filter(Lead.id == lead.id).first()
                    
                    # 1. Enrichment if website exists
                    if l_inst.website:
                        try:
                            analyzer = WebsiteAnalyzer(timeout=10)
                            audit = asyncio.run(analyzer.analyze(l_inst.website))
                            l_inst.website_status = audit.get("website_status")
                            l_inst.website_title = audit.get("website_title")
                            l_inst.website_description = audit.get("website_description")
                            l_inst.ssl_enabled = audit.get("ssl_enabled")
                            l_inst.technology_stack = audit.get("technology_stack")
                            l_inst.chatbot_detected = audit.get("chatbot_detected")
                            l_inst.whatsapp_detected = audit.get("whatsapp_detected")
                            l_inst.ecommerce_detected = audit.get("ecommerce_detected")
                            l_inst.ecommerce_platform = audit.get("ecommerce_platform")
                            if not l_inst.email and audit.get("emails_found"):
                                l_inst.email = audit["emails_found"][0]
                        except Exception as e:
                            pass
                    
                    # 2. Opportunity Detection
                    lead_dict = {
                        "business_name": l_inst.business_name,
                        "industry": l_inst.industry or l_inst.business_category,
                        "website": l_inst.website,
                        "technology_stack": l_inst.technology_stack or []
                    }
                    opp_det = OpportunityDetector()
                    opp_res = opp_det.detect(lead_dict)
                    l_inst.primary_opportunity = opp_res.get("primary_opportunity")
                    l_inst.secondary_opportunities = opp_res.get("secondary_opportunities")
                    l_inst.opportunity_reason = opp_res.get("opportunity_reason")

                    # 3. Scoring
                    lead_dict.update({
                        "primary_opportunity": l_inst.primary_opportunity,
                        "rating": l_inst.rating,
                        "review_count": l_inst.review_count,
                        "email": l_inst.email,
                        "phone": l_inst.phone
                    })
                    scorer = LeadScorer()
                    score_res = scorer.score(lead_dict)
                    l_inst.lead_score = score_res["lead_score"]
                    l_inst.score_breakdown = score_res["score_breakdown"]
                    l_inst.outreach_confidence = score_res["outreach_confidence"]
                    l_inst.pipeline_status = "ANALYZED"
                    
                    db.commit()
                    db.close()
                    st.success("Lead intelligence updated!")
                    st.rerun()

        with btn_col2:
            if st.button("✍️ Generate AI Email", key=f"email_{lead.id}", use_container_width=True):
                with st.spinner("Drafting evidence-based outreach email..."):
                    db = get_db()
                    l_inst = db.query(Lead).filter(Lead.id == lead.id).first()
                    generator = EmailGenerator()
                    lead_payload = {
                        "business_name": l_inst.business_name,
                        "industry": l_inst.industry,
                        "website": l_inst.website,
                        "primary_opportunity": l_inst.primary_opportunity or "Website & Automation Services",
                        "opportunity_reason": l_inst.opportunity_reason or "Enhance client booking and web conversions."
                    }
                    gen_res = generator.generate(lead_payload)
                    l_inst.generated_subject = gen_res.get("subject")
                    l_inst.generated_email = gen_res.get("email")
                    l_inst.email_status = "pending"
                    l_inst.approved = False
                    db.commit()
                    db.close()
                    st.success("Outreach email drafted! Visit Email Review to approve.")
                    st.rerun()

        with btn_col3:
            if lead.generated_email:
                with st.popover("👁️ Preview Email"):
                    st.markdown(f"**Subject:** {lead.generated_subject}")
                    st.text_area("Body", value=lead.generated_email or "", height=150, disabled=True)
            else:
                st.button("No Email Drafted", disabled=True, key=f"noemail_{lead.id}", use_container_width=True)

        with btn_col4:
            if st.button("🗑️ Delete Lead", key=f"del_{lead.id}", use_container_width=True):
                db = get_db()
                repo_del = LeadRepository(db)
                repo_del.delete_lead(lead.id)
                db.close()
                st.warning(f"Deleted {lead.business_name}")
                st.rerun()
