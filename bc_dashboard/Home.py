# Home.py

import streamlit as st
from db_utils import query_home_stats, query_top_performers, query_attention_items

st.set_page_config(
    page_title="Brookfield Comfort Dashboard",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Brookfield Comfort Dashboard")
st.subheader("Welcome to your internal reporting tool.")

# Load data
try:
    stats = query_home_stats()
    top_performers = query_top_performers()
    attention_items = query_attention_items()

    st.markdown("---")

    # Placeholder for future charts and analytics
    st.markdown("## Analytics Dashboard")
    st.info("📊 Charts and analytics coming soon - will include multi-platform insights when Amazon integration is added")

except Exception as e:
    st.error(f"Error loading dashboard data: {e}")
    st.markdown("---")
    st.write("Fallback navigation:")

st.markdown("---")
st.markdown(
    """
    Use the sidebar to navigate between different dashboards:
    - **Home**: This page with top performers and action items
    - **Shopify Health Check**: Detailed SKU-level analysis with filtering

    **Coming Soon**: Amazon dashboard for multi-platform management
    """
)

st.info(
    "Tip: You can expand/collapse the sidebar to focus on the data."
)
