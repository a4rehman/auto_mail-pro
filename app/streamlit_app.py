import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="100Solutionz | Lead Intelligence Platform",
    page_icon="??",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("100Solutionz Lead Intelligence Platform")
st.markdown("AI-Powered Lead Generation & Outreach")

st.info("Navigate using the sidebar to explore the platform.")
