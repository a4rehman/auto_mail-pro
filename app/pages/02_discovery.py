import sys
from pathlib import Path
import pandas as pd
import streamlit as st

# Add project root to sys.path
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.ui_utils import init_page, get_db
from database.repository import LeadRepository
from discovery.discovery_service import DiscoveryService
from core.config_loader import load_yaml
from config.settings import settings

init_page("Lead Discovery", "🔍")

# Load configuration options
industries_cfg = load_yaml("config/industries.yaml")
industry_list = industries_cfg.get("industries", ["dental_clinic", "med_spa", "real_estate", "ecommerce", "gym_fitness", "restaurant", "local_business"])

locations_cfg = load_yaml("config/locations.yaml")
us_states = locations_cfg.get("countries", {}).get("US", {}).get("states", ["TX", "CA", "FL", "NY", "IL", "WA"])

tab1, tab2, tab3 = st.tabs(["🌐 Google Maps Search", "✍️ Manual Lead Entry", "📁 CSV / Excel Import"])

# ==========================================
# TAB 1: GOOGLE MAPS SEARCH
# ==========================================
with tab1:
    st.markdown("### Targeted Prospect Discovery")
    st.caption("Discover local businesses matching your target industry, geography, and review profile.")

    apify_configured = bool(settings.APIFY_API_TOKEN and settings.APIFY_ACTOR_ID)
    
    if not apify_configured:
        st.warning("⚠️ **Apify API Token or Actor ID is not configured in settings.** Simulated Discovery mode is enabled by default so you can test discovery and ingestion without credentials.")

    with st.form("discovery_form"):
        col1, col2 = st.columns(2)
        with col1:
            selected_industry = st.selectbox(
                "Target Industry / Category",
                options=industry_list,
                format_func=lambda x: x.replace("_", " ").title()
            )
            keyword = st.text_input("Custom Keyword (Optional)", placeholder="e.g. Invisalign, Luxury Spa, Roastery")
            country = st.selectbox("Country", ["USA", "UK", "Canada", "Australia"])
        
        with col2:
            state = st.selectbox("State / Region", us_states)
            city = st.text_input("City", value="Austin")
            max_results = st.slider("Maximum Results", min_value=5, max_value=50, value=10, step=5)

        col3, col4 = st.columns(2)
        with col3:
            min_rating = st.slider("Minimum Google Rating", min_value=1.0, max_value=5.0, value=4.0, step=0.1)
        with col4:
            min_reviews = st.number_input("Minimum Reviews Count", min_value=0, max_value=1000, value=10)

        use_simulated = st.checkbox("Use Simulated Demo Scraper (Offline Testing)", value=not apify_configured)

        submitted = st.form_submit_button("🚀 Start Discovery Search", type="primary", use_container_width=True)

    if submitted:
        discovery_params = {
            "industry": selected_industry,
            "keyword": keyword,
            "country": country,
            "state": state,
            "city": city,
            "max_results": max_results,
            "min_rating": min_rating,
            "min_reviews": min_reviews
        }

        service = DiscoveryService()

        with st.spinner("Scraping and analyzing prospect profiles..."):
            try:
                if use_simulated or not apify_configured:
                    results = service.generate_mock_leads(discovery_params)
                else:
                    results = service.discover_leads(discovery_params)
                
                st.session_state["discovered_leads"] = results
                st.success(f"Successfully discovered {len(results)} prospects!")
            except Exception as e:
                st.error(f"Discovery error: {e}. Falling back to simulated leads for demonstration.")
                results = service.generate_mock_leads(discovery_params)
                st.session_state["discovered_leads"] = results

    if "discovered_leads" in st.session_state and st.session_state["discovered_leads"]:
        leads = st.session_state["discovered_leads"]
        st.write("")
        st.markdown(f"#### Discovered Prospects ({len(leads)})")

        df_preview = pd.DataFrame(leads)
        show_cols = [c for c in ["business_name", "industry", "city", "website", "phone", "rating", "review_count"] if c in df_preview.columns]
        st.dataframe(df_preview[show_cols], use_container_width=True)

        col_save, col_clear = st.columns([3, 1])
        with col_save:
            if st.button("💾 Deduplicate & Save All Discovered Leads to Database", type="primary", use_container_width=True):
                db = get_db()
                repo = LeadRepository(db)
                added_count = 0
                updated_count = 0
                for lead_dict in leads:
                    _, is_new = repo.create_or_update(lead_dict)
                    if is_new:
                        added_count += 1
                    else:
                        updated_count += 1
                db.close()
                st.success(f"Processing complete! Added **{added_count} new leads**, updated **{updated_count} existing leads** (deduplicated by domain/email/phone).")
        with col_clear:
            if st.button("Clear Results", use_container_width=True):
                st.session_state["discovered_leads"] = []
                st.rerun()

# ==========================================
# TAB 2: MANUAL PROSPECT ENTRY
# ==========================================
with tab2:
    st.markdown("### Add Single Prospect")
    st.caption("Manually enter a target prospect to run through the intelligence and outreach engine.")

    with st.form("manual_lead_form"):
        mc1, mc2 = st.columns(2)
        with mc1:
            name = st.text_input("Business Name *", placeholder="Acme Dental Solutions")
            website = st.text_input("Website URL", placeholder="https://www.acmedental.com")
            email = st.text_input("Email Address", placeholder="drsmith@acmedental.com")
            phone = st.text_input("Phone Number", placeholder="+1 (555) 123-4567")
            industry_val = st.selectbox("Industry", options=industry_list, format_func=lambda x: x.replace("_", " ").title())

        with mc2:
            city_val = st.text_input("City", "Dallas")
            state_val = st.text_input("State", "TX")
            address_val = st.text_input("Street Address", "100 Main St")
            rating_val = st.number_input("Google Rating", min_value=0.0, max_value=5.0, value=4.5, step=0.1)
            review_val = st.number_input("Review Count", min_value=0, max_value=10000, value=45)

        man_submit = st.form_submit_button("➕ Save Prospect to Database", type="primary", use_container_width=True)

    if man_submit:
        if not name:
            st.error("Business name is required.")
        else:
            db = get_db()
            repo = LeadRepository(db)
            lead_data = {
                "business_name": name,
                "website": website,
                "email": email,
                "phone": phone,
                "industry": industry_val,
                "business_category": industry_val.replace("_", " ").title(),
                "city": city_val,
                "state": state_val,
                "address": address_val,
                "rating": rating_val,
                "review_count": review_val,
                "source": "manual_entry",
                "pipeline_status": "DISCOVERED"
            }
            lead, is_new = repo.create_or_update(lead_data)
            db.close()
            if is_new:
                st.success(f"✓ Lead '{name}' successfully created (ID: {lead.id})!")
            else:
                st.info(f"Existing lead found! Record updated (ID: {lead.id}).")

# ==========================================
# TAB 3: CSV IMPORT
# ==========================================
with tab3:
    st.markdown("### Bulk Prospect Import")
    st.caption("Upload a CSV file containing leads. Columns will be automatically matched.")

    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
    if uploaded_file:
        try:
            df_upload = pd.read_csv(uploaded_file)
            st.write(f"Loaded **{len(df_upload)} rows**. Preview:")
            st.dataframe(df_upload.head(5), use_container_width=True)

            if st.button("🚀 Ingest & Deduplicate All Rows", type="primary"):
                db = get_db()
                repo = LeadRepository(db)
                imported = 0
                for _, row in df_upload.iterrows():
                    r_dict = row.to_dict()
                    lead_payload = {
                        "business_name": r_dict.get("business_name") or r_dict.get("name") or r_dict.get("title") or "Unnamed",
                        "website": r_dict.get("website") or r_dict.get("url") or "",
                        "email": r_dict.get("email") or "",
                        "phone": str(r_dict.get("phone") or ""),
                        "city": str(r_dict.get("city") or ""),
                        "state": str(r_dict.get("state") or ""),
                        "industry": str(r_dict.get("industry") or r_dict.get("category") or "local_business"),
                        "source": "csv_import"
                    }
                    if lead_payload["business_name"] != "Unnamed":
                        _, is_new = repo.create_or_update(lead_payload)
                        if is_new:
                            imported += 1
                db.close()
                st.success(f"Successfully imported {imported} new unique leads into database!")
        except Exception as err:
            st.error(f"Error parsing file: {err}")
