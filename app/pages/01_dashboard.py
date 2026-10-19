import sys
from pathlib import Path
import pandas as pd
import streamlit as st

# Add project root to sys.path
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.ui_utils import init_page, get_db, render_score_badge, seed_demo_leads
from database.repository import LeadRepository
from exports.excel_export import ExcelExporter
from exports.csv_export import CSVExporter

init_page("Platform Dashboard", "📊")

db = get_db()
repo = LeadRepository(db)
metrics = repo.get_metrics()
leads = repo.list_leads(limit=500)
db.close()

# Metric summary row
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Leads", metrics["total_leads"], delta="In Database")
c2.metric("High Score (≥80)", metrics["high_score"], delta="Priority Targets")
c3.metric("Awaiting Review", metrics["pending_review"], delta="Needs Approval")
c4.metric("Ready in Queue", metrics["ready_outreach"], delta="Approved")
c5.metric("Outreach Dispatched", metrics["emails_sent"], delta="Dispatched")

st.divider()

if not leads:
    st.info("No leads available in the database yet. Click below to load realistic sample leads or navigate to Lead Discovery.")
    if st.button("🌱 Load Sample B2B Leads", type="primary"):
        db = get_db()
        added = seed_demo_leads(db)
        db.close()
        st.success(f"Added {added} sample leads!")
        st.rerun()
else:
    # Build dataframe for analysis
    lead_rows = []
    for l in leads:
        lead_rows.append({
            "ID": l.id,
            "Business Name": l.business_name,
            "Industry": (l.business_category or l.industry or "General").replace("_", " ").title(),
            "City": l.city or "N/A",
            "State": l.state or "N/A",
            "Score": l.lead_score or 0,
            "Opportunity": l.primary_opportunity or "Not evaluated",
            "Pipeline Status": l.pipeline_status or "DISCOVERED",
            "Approved": "Yes" if l.approved else "No",
            "Email Status": l.email_status or "pending",
            "Contact Status": l.contact_status or "new",
            "Website": l.website or ""
        })
    df = pd.DataFrame(lead_rows)

    # Charts Row
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("🏢 Leads by Industry")
        ind_counts = df["Industry"].value_counts()
        st.bar_chart(ind_counts, color="#6366F1")

    with col_chart2:
        st.subheader("🎯 Lead Score Distribution")
        score_bins = pd.cut(df["Score"], bins=[-1, 49, 79, 100], labels=["Low (<50)", "Medium (50-79)", "High (80-100)"])
        score_counts = score_bins.value_counts().sort_index()
        st.bar_chart(score_counts, color="#10B981")

    st.write("")

    # Status distribution row
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.subheader("🔄 Pipeline Status")
        st.dataframe(df["Pipeline Status"].value_counts().rename_axis("Stage").reset_index(name="Count"), use_container_width=True)

    with col_stat2:
        st.subheader("💡 Top Commercial Opportunities")
        top_opps = df[df["Opportunity"] != "Not evaluated"]["Opportunity"].value_counts().head(5)
        if not top_opps.empty:
            st.dataframe(top_opps.rename_axis("Opportunity").reset_index(name="Count"), use_container_width=True)
        else:
            st.caption("No opportunities identified yet. Run intelligence on leads.")

    st.divider()

    # Data Table with quick search
    st.subheader("📋 Lead Registry Overview")
    
    col_filter1, col_filter2, col_export = st.columns([2, 2, 2])
    with col_filter1:
        search_query = st.text_input("🔍 Search by business name or city", "")
    with col_filter2:
        ind_filter = st.selectbox("Filter Industry", ["All"] + sorted(list(df["Industry"].unique())))
    with col_export:
        st.write("")
        # Quick export button
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Registry (CSV)",
            data=csv_data,
            file_name="leads_registry.csv",
            mime="text/csv",
            use_container_width=True
        )

    filtered_df = df
    if search_query:
        filtered_df = filtered_df[
            filtered_df["Business Name"].str.contains(search_query, case=False, na=False) |
            filtered_df["City"].str.contains(search_query, case=False, na=False)
        ]
    if ind_filter != "All":
        filtered_df = filtered_df[filtered_df["Industry"] == ind_filter]

    st.dataframe(
        filtered_df[["ID", "Business Name", "Industry", "City", "State", "Score", "Opportunity", "Pipeline Status", "Approved", "Email Status"]],
        use_container_width=True,
        hide_index=True
    )
