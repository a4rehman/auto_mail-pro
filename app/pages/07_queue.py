import sys
from pathlib import Path
from datetime import datetime
import streamlit as st

# Add project root to sys.path
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.ui_utils import init_page, get_db
from database.models import Lead
from database.repository import LeadRepository
from outreach.sender import EmailSender
from security.compliance import ComplianceManager
from security.suppression import SuppressionList
from config.settings import settings

init_page("Outreach Queue & Dispatcher", "📬")

comp_mgr = ComplianceManager()
compliance = comp_mgr.get_sender_identity()

# Safety banner
if settings.DRY_RUN:
    st.markdown("""
    <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 10px; padding: 14px; margin-bottom: 20px;">
        <h4 style="margin:0 0 4px 0; color: #F59E0B;">🛡️ DRY RUN MODE IS ACTIVE (Safe Simulation)</h4>
        <p style="margin:0; font-size: 0.9rem; color: #FDE68A;">
            All outreach is safely simulated. Sending will log transactions and update lead statuses without transmitting emails over external SMTP networks. To send real emails, toggle DRY_RUN in Settings.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 10px; padding: 14px; margin-bottom: 20px;">
        <h4 style="margin:0 0 4px 0; color: #EF4444;">🚨 LIVE SMTP TRANSMISSION ACTIVE</h4>
        <p style="margin:0; font-size: 0.9rem; color: #FCA5A5;">
            Outreach will be physically transmitted via configured SMTP server ({settings.SMTP_HOST}).
        </p>
    </div>
    """, unsafe_allow_html=True)

db = get_db()
queue_leads = db.query(Lead).filter(
    Lead.approved == True,
    Lead.email_status != "sent",
    Lead.do_not_contact != True
).all()

sent_leads = db.query(Lead).filter(
    Lead.email_status == "sent"
).order_by(Lead.sent_at.desc()).all()
db.close()

c1, c2, c3 = st.columns(3)
c1.metric("Pending in Queue", len(queue_leads))
c2.metric("Dispatched Outreach", len(sent_leads))
c3.metric("Sender Identity", compliance.get("sender_name", "100Solutionz"))

st.divider()

tab_queue, tab_history, tab_compliance = st.tabs(["📤 Active Queue", "📜 Sent History", "⚖️ Compliance & Suppression"])

# ==========================================
# TAB 1: ACTIVE QUEUE
# ==========================================
with tab_queue:
    if not queue_leads:
        st.info("The outreach queue is empty. Visit **Email Review** to approve drafted emails.")
    else:
        st.write(f"**{len(queue_leads)}** approved leads queued for sending.")

        if st.button("🚀 Process & Dispatch All Queued Outreach", type="primary", use_container_width=True):
            sender = EmailSender(dry_run=settings.DRY_RUN)
            progress_bar = st.progress(0, text="Starting dispatch...")
            db = get_db()
            
            dispatched = 0
            for idx, q_lead in enumerate(queue_leads):
                progress_bar.progress((idx + 1) / len(queue_leads), text=f"Sending to {q_lead.business_name} ({q_lead.email})...")
                
                # Retrieve in current db session
                l_item = db.query(Lead).filter(Lead.id == q_lead.id).first()
                if l_item and l_item.email:
                    try:
                        res = sender.send(
                            to_email=l_item.email,
                            subject=l_item.generated_subject or "Partnership Opportunity",
                            body=l_item.generated_email or ""
                        )
                        l_item.email_status = "sent"
                        l_item.contact_status = "contacted"
                        l_item.sent_at = datetime.utcnow()
                        l_item.pipeline_status = "SENT"
                        dispatched += 1
                    except Exception as err:
                        st.error(f"Failed to dispatch to {l_item.email}: {err}")
            
            db.commit()
            db.close()
            st.success(f"Outreach batch finished! Successfully dispatched {dispatched} messages.")
            st.rerun()

        st.write("")
        st.markdown("#### Queued Prospects")
        for q in queue_leads:
            with st.container():
                st.markdown(f"""
                <div class="lead-card">
                    <div style="display:flex; justify-content:space-between;">
                        <strong>🏢 {q.business_name}</strong>
                        <span class="system-pill pill-active">To: {q.email or 'Missing Email'}</span>
                    </div>
                    <p style="margin:4px 0; font-size:0.9rem;"><strong>Subject:</strong> {q.generated_subject}</p>
                    <p style="margin:0; font-size:0.85rem; color:#9CA3AF;">{q.generated_email[:120]}...</p>
                </div>
                """, unsafe_allow_html=True)

# ==========================================
# TAB 2: SENT HISTORY
# ==========================================
with tab_history:
    if not sent_leads:
        st.info("No outreach emails have been dispatched yet.")
    else:
        st.write(f"Total dispatched: **{len(sent_leads)}**")
        for s in sent_leads:
            with st.expander(f"✉️ {s.business_name} — Sent: {s.sent_at.strftime('%Y-%m-%d %H:%M') if s.sent_at else 'Recent'}"):
                st.markdown(f"**Recipient:** `{s.email}`")
                st.markdown(f"**Subject:** {s.generated_subject}")
                st.text_area("Message Sent", value=s.generated_email or "", height=120, disabled=True)

# ==========================================
# TAB 3: COMPLIANCE & SUPPRESSION
# ==========================================
with tab_compliance:
    st.markdown("#### ⚖️ Compliance Identity (CAN-SPAM / GDPR)")
    st.markdown(f"""
    - **Sender Name:** `{compliance.get('sender_name')}`
    - **Sender Email:** `{compliance.get('sender_email') or 'Not configured in settings'}`
    - **Business Address:** `{compliance.get('business_address') or '100Solutionz HQ'}`
    - **Unsubscribe Link:** `{'Enabled' if compliance.get('unsubscribe_enabled') else 'Disabled'}`
    """)

    st.write("")
    st.markdown("#### 🚫 Add to Suppression List")
    st.caption("Suppressed addresses are globally excluded from receiving cold outreach.")

    supp_email = st.text_input("Email to Suppress", placeholder="unsub@target.com")
    supp_reason = st.selectbox("Reason", ["Unsubscribed", "Bounced / Invalid", "Wrong Contact", "Manual Request"])

    if st.button("Add to Suppression"):
        if supp_email:
            db = get_db()
            matched = db.query(Lead).filter(Lead.email == supp_email.strip().lower()).all()
            for m in matched:
                m.do_not_contact = True
                m.suppression_reason = supp_reason
                m.suppressed_at = datetime.utcnow()
            db.commit()
            db.close()
            st.success(f"Suppressed {supp_email} ({len(matched)} matching leads updated).")
        else:
            st.warning("Enter a valid email address.")
