import streamlit as st
import requests

st.set_page_config(
    page_title="LMIP Dashboard",
    page_icon="🌕",
    layout="wide",
)

st.title("Lunar Mission Intelligence Platform (LMIP)")
st.subheader("AI-Assisted Decision Support System for Autonomous Lunar Polar Exploration")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### System Status")
    try:
        response = requests.get("http://backend:8000/health", timeout=5)
        if response.status_code == 200:
            st.success("Backend Connection: OK")
        else:
            st.warning("Backend Connection: Failed (Non-200 status)")
    except Exception as e:
        st.error(f"Backend Connection: Failed ({e})")
        
with col2:
    st.markdown("### Mission Overview")
    st.info("No data loaded. Please proceed to data ingestion.")
    
st.markdown("---")
st.markdown("LMIP Dashboard v1.0.0")
