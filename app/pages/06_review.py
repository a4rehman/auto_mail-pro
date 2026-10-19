import sys
from pathlib import Path
import streamlit as st

# Add project root to sys.path
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.ui_utils import init_page, get_db, render_score_badge
from database.repository import LeadRepository
from database.models import Lead
from outreach.email_validator import EmailValidator
from outreach.email_generator import EmailGenerator

init_page("Email Review & Human Approval", "✍️")

st.markdown("### Human-in-the-Loop Approval Workflow")
st.caption("Review, edit, and approve personalized AI outreach messages prior to queue dispatch. Safety standards enforce evidence-based claims and prohibit unreplaced template placeholders.")

db = get_db()
pending_leads = db.query(Lead).filter(
    Lead.generated_email.isnot(None),
    (Lead.approved == False) | (Lead.approved.is_(None))
).all()

approved_leads = db.query(Lead).filter(
    Lead.approved == True,
    Lead.email_status != "sent"
).all()
db.close()

c1, c2 = st.columns(2)
c1.metric("Pending Human Review", len(pending_leads))
c2.metric("Approved & In Queue", len(approved_leads))

st.divider()

tab_pending, tab_approved = st.tabs(["⏳ Pending Approval", "✅ Approved Queue Ready"])

# ==========================================
# TAB 1: PENDING APPROVAL
# ==========================================
with tab_pending:
    if not pending_leads:
        st.success("🎉 All drafted emails have been reviewed! No pending emails.")
        st.info("To generate more emails, visit the **Lead Database** or **Website Intelligence** and click 'Generate AI Email'.")
    else:
        # Batch Approve button
        if st.button("🚀 Batch Approve All Pending Emails", type="primary"):
            db = get_db()
            for l in pending_leads:
                l_rec = db.query(Lead).filter(Lead.id == l.id).first()
                l_rec.approved = True
                l_rec.pipeline_status = "APPROVED"
                l_rec.contact_status = "ready"
            db.commit()
            db.close()
            st.success(f"Approved all {len(pending_leads)} emails!")
            st.rerun()

        st.write("")

        validator = EmailValidator()

        for lead in pending_leads:
            with st.container():
                st.markdown(f"""
                <div class="lead-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0; color:#818CF8;">🏢 {lead.business_name}</h4>
                        <span class="system-pill pill-neutral">Score: {lead.lead_score or 'N/A'}</span>
                    </div>
                    <p style="margin:4px 0; color:#9CA3AF; font-size:0.85rem;">
                        Target Email: <code>{lead.email or 'No email on file'}</code> • Website: {lead.website or 'N/A'}
                    </p>
                    <p style="margin:4px 0; color:#10B981; font-size:0.88rem;">
                        🎯 <strong>Opportunity:</strong> {lead.primary_opportunity or 'General Service Fit'}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                col_edit, col_eval = st.columns([3, 2])

                with col_edit:
                    subj_key = f"subj_{lead.id}"
                    body_key = f"body_{lead.id}"

                    subj_val = st.text_input("Subject Line", value=lead.generated_subject or "", key=subj_key)
                    body_val = st.text_area("Email Content", value=lead.generated_email or "", height=170, key=body_key)

                with col_eval:
                    st.markdown("##### 🔍 Automated Safety Check")
                    val_res = validator.validate(subj_val, body_val)
                    
                    word_count = len(body_val.split())
                    has_placeholders = any(p in body_val for p in ["[Name]", "[Business]", "[Company]", "{"])

                    if not has_placeholders and word_count <= 130:
                        st.success("✅ **Quality Check: PASSED**\n- No placeholder leaks detected\n- Concise length (< 130 words)\n- Natural tone")
                    else:
                        st.warning("⚠️ **Review Flags:**")
                        if has_placeholders:
                            st.write("- ❌ Unreplaced placeholder detected!")
                        if word_count > 130:
                            st.write(f"- ⚠️ Word count ({word_count} words) is longer than 120 target.")

                    st.caption(f"Word count: {word_count} words")

                # Action buttons
                b1, b2, b3 = st.columns([2, 1.5, 1.5])
                with b1:
                    if st.button("✅ Approve & Queue for Outreach", key=f"app_{lead.id}", type="primary", use_container_width=True):
                        db = get_db()
                        l_rec = db.query(Lead).filter(Lead.id == lead.id).first()
                        l_rec.generated_subject = subj_val
                        l_rec.generated_email = body_val
                        l_rec.approved = True
                        l_rec.pipeline_status = "APPROVED"
                        l_rec.contact_status = "ready"
                        db.commit()
                        db.close()
                        st.success(f"Approved email for {lead.business_name}!")
                        st.rerun()

                with b2:
                    if st.button("🔄 Regenerate", key=f"regen_{lead.id}", use_container_width=True):
                        with st.spinner("Regenerating with AI..."):
                            generator = EmailGenerator()
                            gen = generator.generate({
                                "business_name": lead.business_name,
                                "industry": lead.industry,
                                "website": lead.website,
                                "primary_opportunity": lead.primary_opportunity or "Website Development",
                                "opportunity_reason": lead.opportunity_reason or ""
                            })
                            db = get_db()
                            l_rec = db.query(Lead).filter(Lead.id == lead.id).first()
                            l_rec.generated_subject = gen.get("subject")
                            l_rec.generated_email = gen.get("email")
                            db.commit()
                            db.close()
                            st.rerun()

                with b3:
                    if st.button("❌ Reject / Suppress", key=f"rej_{lead.id}", use_container_width=True):
                        db = get_db()
                        l_rec = db.query(Lead).filter(Lead.id == lead.id).first()
                        l_rec.approved = False
                        l_rec.do_not_contact = True
                        l_rec.suppression_reason = "Rejected in review"
                        db.commit()
                        db.close()
                        st.warning(f"Rejected {lead.business_name}")
                        st.rerun()

                st.divider()

# ==========================================
# TAB 2: APPROVED QUEUE READY
# ==========================================
with tab_approved:
    if not approved_leads:
        st.info("No approved leads waiting in queue.")
    else:
        st.write(f"**{len(approved_leads)}** leads approved and ready for dispatch in Outreach Queue.")
        for l_app in approved_leads:
            with st.expander(f"✅ {l_app.business_name} — {l_app.generated_subject}"):
                st.markdown(f"**To:** `{l_app.email}`")
                st.text_area("Approved Email", value=l_app.generated_email or "", height=120, disabled=True)
                if st.button("↩️ Revoke Approval", key=f"rev_{l_app.id}"):
                    db = get_db()
                    l_rec = db.query(Lead).filter(Lead.id == l_app.id).first()
                    l_rec.approved = False
                    l_rec.contact_status = "new"
                    db.commit()
                    db.close()
                    st.info(f"Revoked approval for {l_app.business_name}")
                    st.rerun()
