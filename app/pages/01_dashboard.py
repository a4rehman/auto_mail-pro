import streamlit as st

st.title('Dashboard')
col1, col2, col3, col4 = st.columns(4)
col1.metric('Total Leads', 0)
col2.metric('High Score (>=80)', 0)
col3.metric('Ready for Outreach', 0)
col4.metric('Emails Sent', 0)
