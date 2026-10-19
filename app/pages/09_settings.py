import sys
from pathlib import Path
import os
import streamlit as st

# Add project root to sys.path
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.ui_utils import init_page, get_db, seed_demo_leads
from database.models import Lead
from database.repository import LeadRepository
from config.settings import settings

init_page("System Settings & Configuration", "⚙️")

tab_api, tab_smtp, tab_db = st.tabs(["🔑 API & AI Engines", "✉️ SMTP & Safety Controls", "🗄️ Database Management"])

# ==========================================
# TAB 1: API & AI ENGINES
# ==========================================
with tab_api:
    st.markdown("### Third-Party Service Credentials")
    st.caption("Configure API tokens for Apify scraper actors and OpenAI language models. Changes can be saved to your local session or `.env`.")

    with st.form("api_config_form"):
        st.markdown("##### 🌐 Apify Configuration")
        apify_token = st.text_input("Apify API Token", value=settings.APIFY_API_TOKEN, type="password")
        apify_actor = st.text_input("Apify Google Maps Actor ID", value=settings.APIFY_ACTOR_ID, placeholder="compass/crawler-google-places")

        st.markdown("##### 🧠 OpenAI Configuration")
        openai_key = st.text_input("OpenAI API Key", value=settings.OPENAI_API_KEY, type="password")
        ai_model = st.selectbox("AI Model", ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"], index=0)
        ai_temp = st.slider("Temperature", 0.0, 1.0, float(settings.AI_TEMPERATURE), 0.05)

        save_api = st.form_submit_button("💾 Save API Credentials", type="primary")

    if save_api:
        settings.APIFY_API_TOKEN = apify_token
        settings.APIFY_ACTOR_ID = apify_actor
        settings.OPENAI_API_KEY = openai_key
        settings.AI_MODEL = ai_model
        settings.AI_TEMPERATURE = ai_temp
        st.success("API configuration updated successfully in active session!")

    st.write("")
    st.markdown("##### 🩺 Diagnostics & Connectivity")
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        if st.button("Test Apify Configuration"):
            if settings.APIFY_API_TOKEN:
                st.success("Apify Token present.")
            else:
                st.warning("Apify Token is currently empty. Discovery will run in simulated demo mode.")
    with d_col2:
        if st.button("Test OpenAI Configuration"):
            if settings.OPENAI_API_KEY:
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=settings.OPENAI_API_KEY)
                    resp = client.chat.completions.create(
                        model=settings.AI_MODEL,
                        messages=[{"role": "user", "content": "ping"}],
                        max_tokens=5
                    )
                    st.success("OpenAI connection successful!")
                except Exception as err:
                    st.error(f"OpenAI test failed: {err}")
            else:
                st.warning("OpenAI API Key is empty. Default fallback templates will be used for drafting.")

# ==========================================
# TAB 2: SMTP & SAFETY CONTROLS
# ==========================================
with tab_smtp:
    st.markdown("### Outreach Dispatch & Compliance")

    with st.form("smtp_form"):
        st.markdown("##### 🛡️ Safety Switches")
        dry_run = st.toggle("Enable DRY RUN Mode (Recommended for testing)", value=settings.DRY_RUN, help="When enabled, no real emails are sent via SMTP.")
        unsub = st.toggle("Include Unsubscribe Header / Footer (CAN-SPAM)", value=settings.UNSUBSCRIBE_ENABLED)

        st.markdown("##### ✉️ SMTP Credentials")
        s_host = st.text_input("SMTP Host", value=settings.SMTP_HOST)
        s_port = st.number_input("SMTP Port", value=settings.SMTP_PORT)
        s_user = st.text_input("SMTP Username / Email", value=settings.SMTP_USER)
        s_pass = st.text_input("SMTP Password / App Password", value=settings.SMTP_PASS, type="password")
        s_name = st.text_input("Sender Display Name", value=settings.SENDER_NAME)
        s_from = st.text_input("Sender Email Address", value=settings.SENDER_EMAIL)

        st.markdown("##### 🏢 Compliance Identity")
        b_name = st.text_input("Business Name", value=settings.BUSINESS_NAME)
        b_addr = st.text_input("Physical Business Address", value=settings.BUSINESS_ADDRESS, placeholder="100 Innovation Way, Suite 400, Austin, TX 78701")

        save_smtp = st.form_submit_button("💾 Save Outreach Settings", type="primary")

    if save_smtp:
        settings.DRY_RUN = dry_run
        settings.UNSUBSCRIBE_ENABLED = unsub
        settings.SMTP_HOST = s_host
        settings.SMTP_PORT = s_port
        settings.SMTP_USER = s_user
        settings.SMTP_PASS = s_pass
        settings.SENDER_NAME = s_name
        settings.SENDER_EMAIL = s_from
        settings.BUSINESS_NAME = b_name
        settings.BUSINESS_ADDRESS = b_addr
        st.success("Outreach and compliance settings saved in active session!")

# ==========================================
# TAB 3: DATABASE MANAGEMENT
# ==========================================
with tab_db:
    st.markdown("### Local Database Controls")
    
    db = get_db()
    lead_count = db.query(Lead).count()
    db.close()

    st.markdown(f"**Database URI:** `{settings.DATABASE_URL}`")
    st.markdown(f"**Total Records:** `{lead_count} Leads`")

    st.write("")
    col_db1, col_db2 = st.columns(2)

    with col_db1:
        st.markdown("##### 🌱 Sample Lead Generation")
        st.caption("Populate the database with curated B2B leads across multiple verticals with complete websites, intelligence, and email drafts.")
        if st.button("Load Curated Sample Leads", type="primary"):
            db = get_db()
            added = seed_demo_leads(db)
            db.close()
            st.success(f"Added {added} sample leads to the registry!")
            st.rerun()

    with col_db2:
        st.markdown("##### 🧹 Database Reset")
        st.caption("Clear all leads and reset the local database. Warning: this action cannot be undone.")
        confirm_del = st.checkbox("I confirm I want to wipe all leads")
        if st.button("Delete All Leads", type="secondary", disabled=not confirm_del):
            db = get_db()
            db.query(Lead).delete()
            db.commit()
            db.close()
            st.warning("All leads have been wiped from the database.")
            st.rerun()
