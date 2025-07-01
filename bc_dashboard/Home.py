# Home.py

import streamlit as st

st.set_page_config(
    page_title="Brookfield Comfort Dashboard",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Brookfield Comfort Dashboard")
st.subheader("Welcome to your internal reporting tool.")

st.markdown(
    """
    Use the sidebar to navigate between different dashboards:
    - **Home**: This page
    - **Shopify Health Check**: Detailed SKU-level stock and pricing insights
    """
)

st.info(
    "Tip: You can expand/collapse the sidebar to focus on the data."
)

st.markdown("---")
st.write("Future ideas for this Home page:")
st.markdown("""
- High-level summary KPIs (total SKUs, low stock, pricing errors)
- Quick links to actions
- Recent updates
""")
