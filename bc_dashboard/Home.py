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

    # Key Metrics Row
    st.markdown("## Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total SKUs", f"{int(stats['total_skus'])}")
        percentage_100_plus = (stats['skus_100_plus'] / stats['total_skus'] * 100) if stats['total_skus'] > 0 else 0
        st.metric("£100+ Annual Profit", f"{int(stats['skus_100_plus'])} ({percentage_100_plus:.1f}%)")

    with col2:
        st.metric("Winners", f"{int(stats['winners'])}")
        st.metric("Losers", f"{int(stats['losers'])}")

    with col3:
        st.metric("Needs Attention", f"{int(stats['needs_attention'])}")
        st.metric("Low Stock (<5)", f"{int(stats['low_stock'])}")

    with col4:
        st.metric("No Sales 30d", f"{int(stats['no_sales_30d'])}")
        st.metric("No Sales 90d", f"{int(stats['no_sales_90d'])}")

    with col5:
        st.metric("Local Stock Units", f"{int(stats['total_local_stock'])}")
        velocity_formatted = f"{stats['avg_sales_velocity']:.2f}" if stats['avg_sales_velocity'] else "0.00"
        st.metric("Avg Daily Velocity", velocity_formatted)

    st.markdown("---")

    # Two column layout for detailed tables
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("## Top Performers (Annual Profit)")
        if not top_performers.empty:
            # Format the dataframe for display
            display_df = top_performers.copy()
            display_df['annual_profit'] = display_df['annual_profit'].apply(lambda x: f"£{x:,.0f}" if x else "£0")
            display_df['sales_velocity_per_day'] = display_df['sales_velocity_per_day'].apply(lambda x: f"{x:.2f}" if x else "0.00")

            st.dataframe(
                display_df[['code', 'brand', 'segment', 'annual_profit', 'sales_30d', 'local_stock']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No data available")

    with col_right:
        st.markdown("## Items Needing Attention")
        if not attention_items.empty:
            # Format the dataframe for display
            display_df = attention_items.copy()
            display_df['annual_profit'] = display_df['annual_profit'].apply(lambda x: f"£{x:,.0f}" if x else "£0")

            st.dataframe(
                display_df[['code', 'brand', 'recommended_action', 'annual_profit', 'total_stock', 'sales_30d']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("All items are OK")

except Exception as e:
    st.error(f"Error loading dashboard data: {e}")
    st.markdown("---")
    st.write("Fallback navigation:")

st.markdown("---")
st.markdown(
    """
    Use the sidebar to navigate between different dashboards:
    - **Home**: This page with key metrics and top performers
    - **Shopify Health Check**: Detailed SKU-level stock and pricing insights
    """
)

st.info(
    "Tip: You can expand/collapse the sidebar to focus on the data."
)
