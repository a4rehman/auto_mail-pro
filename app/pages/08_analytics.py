import sys
from pathlib import Path
import pandas as pd
import streamlit as st

# Add project root to sys.path
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.ui_utils import init_page, get_db
from database.models import Lead

init_page("Platform Analytics & Intelligence Metrics", "📈")

db = get_db()
leads = db.query(Lead).all()
db.close()

if not leads:
    st.info("No leads available to compute analytics. Please discover or seed leads first.")
    st.stop()

# Convert leads to DataFrame
data = []
for l in leads:
    data.append({
        "ID": l.id,
        "Business Name": l.business_name,
        "Industry": (l.business_category or l.industry or "General").replace("_", " ").title(),
        "Score": l.lead_score or 0,
        "Rating": l.rating or 0.0,
        "Reviews": l.review_count or 0,
        "Status": l.pipeline_status or "DISCOVERED",
        "Approved": l.approved or False,
        "Email Status": l.email_status or "pending",
        "Opportunity": l.primary_opportunity or "None",
        "Has Tech Stack": bool(l.technology_stack),
        "Chatbot": bool(l.chatbot_detected or l.whatsapp_detected),
        "Ecommerce": bool(l.ecommerce_detected),
        "SSL": bool(l.ssl_enabled)
    })
df = pd.DataFrame(data)

st.markdown("### 🔄 **Pipeline Funnel Velocity**")

# Funnel stages
total_count = len(df)
enriched_count = len(df[df["Has Tech Stack"]])
scored_count = len(df[df["Score"] > 0])
approved_count = len(df[df["Approved"]])
sent_count = len(df[df["Email Status"] == "sent"])

funnel_df = pd.DataFrame([
    {"Stage": "1. Discovered", "Leads": total_count, "Conversion": "100%"},
    {"Stage": "2. Tech Enriched", "Leads": enriched_count, "Conversion": f"{round(enriched_count/total_count*100, 1)}%"},
    {"Stage": "3. Scored (AI)", "Leads": scored_count, "Conversion": f"{round(scored_count/total_count*100, 1)}%"},
    {"Stage": "4. Approved", "Leads": approved_count, "Conversion": f"{round(approved_count/total_count*100, 1)}%"},
    {"Stage": "5. Dispatched", "Leads": sent_count, "Conversion": f"{round(sent_count/total_count*100, 1)}%"}
])

st.dataframe(funnel_df, use_container_width=True, hide_index=True)

st.divider()

col_a1, col_a2 = st.columns(2)

with col_a1:
    st.markdown("#### 🏢 Industry Breakdown")
    ind_data = df["Industry"].value_counts()
    st.bar_chart(ind_data, color="#818CF8")

with col_a2:
    st.markdown("#### 🎯 Score Breakdown")
    score_bins = pd.cut(df["Score"], bins=[-1, 49, 79, 100], labels=["Low (<50)", "Medium (50-79)", "High (80-100)"])
    st.bar_chart(score_bins.value_counts().sort_index(), color="#10B981")

st.divider()

col_b1, col_b2 = st.columns(2)

with col_b1:
    st.markdown("#### 💡 Commercial Opportunities Detected")
    opp_data = df[df["Opportunity"] != "None"]["Opportunity"].value_counts().head(6)
    if not opp_data.empty:
        st.bar_chart(opp_data, color="#F59E0B")
    else:
        st.caption("No opportunities analyzed yet.")

with col_b2:
    st.markdown("#### 🔬 Technology & Infrastructure Adoption")
    tech_stats = {
        "SSL Enabled": df["SSL"].sum(),
        "Chatbot / WhatsApp Present": df["Chatbot"].sum(),
        "E-commerce Platform": df["Ecommerce"].sum(),
        "Tech Stack Fingerprinted": df["Has Tech Stack"].sum()
    }
    st.dataframe(pd.DataFrame(list(tech_stats.items()), columns=["Technology Factor", "Active Count"]), use_container_width=True, hide_index=True)
