import streamlit as st
from db_utils import query_health_check

st.set_page_config(
    page_title="Shopify Health Check",
    page_icon="✅",
    layout="wide"
)

st.title("✅ Shopify Health Check")
st.subheader("Code Level Stock and Price Management")

def filter_dataframe(df, include_text, exclude_text):
    """
    Filter dataframe based on include/exclude text across specified columns.
    Text matching is case-insensitive and partial.
    """
    if df.empty:
        return df

    # Columns to search in (including title if it exists)
    search_columns = ['code', 'brand', 'owner', 'status', 'segment']
    if 'title' in df.columns:
        search_columns.append('title')

    # Start with all data
    filtered_df = df.copy()

    # Apply include filter if text provided
    if include_text.strip():
        include_mask = False
        for col in search_columns:
            if col in filtered_df.columns:
                # Case-insensitive partial match
                col_mask = filtered_df[col].astype(str).str.lower().str.contains(
                    include_text.lower(), na=False, regex=False
                )
                include_mask = include_mask | col_mask
        filtered_df = filtered_df[include_mask]

    # Apply exclude filter if text provided
    if exclude_text.strip():
        exclude_mask = False
        for col in search_columns:
            if col in filtered_df.columns:
                # Case-insensitive partial match
                col_mask = filtered_df[col].astype(str).str.lower().str.contains(
                    exclude_text.lower(), na=False, regex=False
                )
                exclude_mask = exclude_mask | col_mask
        filtered_df = filtered_df[~exclude_mask]

    return filtered_df

def calculate_filter_stats(df):
    """Calculate key statistics for the filtered dataset"""
    if df.empty:
        return {}

    stats = {
        'total_items': len(df),
        'winners': len(df[df['segment'] == 'Winner']) if 'segment' in df.columns else 0,
        'losers': len(df[df['segment'] == 'Loser']) if 'segment' in df.columns else 0,
        'profit_100_plus': len(df[df['annual_profit'] >= 100]) if 'annual_profit' in df.columns else 0,
        'total_annual_profit': df['annual_profit'].sum() if 'annual_profit' in df.columns else 0,
        'avg_annual_profit': df['annual_profit'].mean() if 'annual_profit' in df.columns else 0,
        'total_local_stock': df['local_stock'].sum() if 'local_stock' in df.columns else 0,
        'low_stock': len(df[df['local_stock'] < 5]) if 'local_stock' in df.columns else 0,
        'no_sales_30d': len(df[df['sales_30d'] == 0]) if 'sales_30d' in df.columns else 0,
        'needs_attention': len(df[df['recommended_action'] != 'OK']) if 'recommended_action' in df.columns else 0
    }
    return stats

try:
    # Load all data
    df = query_health_check()

    # Initialize session state for filters
    if 'filtered_df' not in st.session_state:
        st.session_state.filtered_df = df
    if 'filter_applied' not in st.session_state:
        st.session_state.filter_applied = False
    if 'clear_inputs' not in st.session_state:
        st.session_state.clear_inputs = False

    # Filter controls in a clean container
    with st.container():
        # Use form to handle Enter key properly
        with st.form(key="filter_form", clear_on_submit=True):
            col1, col2, col3, col4 = st.columns([3, 3, 1.5, 1.5])

            with col1:
                include_text = st.text_input(
                    "Include (show only items containing this text):",
                    help="Search in: code, brand, owner, status, segment, title"
                )

            with col2:
                exclude_text = st.text_input(
                    "Exclude (hide items containing this text):",
                    help="Search in: code, brand, owner, status, segment, title"
                )

            with col3:
                st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
                filter_clicked = st.form_submit_button("🔍 Filter", help="Apply current filters", use_container_width=True)

            with col4:
                st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
                reset_clicked = st.form_submit_button("🔄 Reset", help="Clear all filters and reload data", use_container_width=True)

    # Handle filter button or form submission (Enter/Tab)
    if filter_clicked or (include_text.strip() or exclude_text.strip()):
        # Apply filters to current filtered dataset (progressive filtering)
        current_df = st.session_state.filtered_df if st.session_state.filter_applied else df
        st.session_state.filtered_df = filter_dataframe(current_df, include_text, exclude_text)
        st.session_state.filter_applied = True

    # Handle reset button
    if reset_clicked:
        # Sort by annual_profit DESC when resetting
        st.session_state.filtered_df = df.sort_values('annual_profit', ascending=False) if 'annual_profit' in df.columns else df
        st.session_state.filter_applied = False

    # Calculate and show statistics
    current_stats = calculate_filter_stats(st.session_state.filtered_df)

    if current_stats:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Items", f"{current_stats['total_items']}")
            percentage_100_plus = (current_stats['profit_100_plus'] / current_stats['total_items'] * 100) if current_stats['total_items'] > 0 else 0
            st.metric("£100+ Profit", f"{current_stats['profit_100_plus']} ({percentage_100_plus:.1f}%)")

        with col2:
            st.metric("Winners", f"{current_stats['winners']}")
            st.metric("Losers", f"{current_stats['losers']}")

        with col3:
            st.metric("Needs Attention", f"{current_stats['needs_attention']}")
            st.metric("Low Stock (<5)", f"{current_stats['low_stock']}")

        with col4:
            st.metric("No Sales 30d", f"{current_stats['no_sales_30d']}")
            avg_profit_formatted = f"£{current_stats['avg_annual_profit']:,.0f}"
            st.metric("Avg Profit", avg_profit_formatted)

    # Show filter results
    if st.session_state.filter_applied:
        st.info(f"Showing {len(st.session_state.filtered_df):,} of {len(df):,} rows after filtering")
    else:
        st.info(f"Showing all {len(df):,} rows (sorted by annual profit)")

    st.markdown("---")

    # Use filtered data
    columns_to_show = [
        "code",
        "brand",
        "owner",
        "status",
        "last_reviewed",
        "notes",
        "sold_qty",
        "annual_profit",
        "profit_per_unit",
        "segment",
        "local_stock",
        "shopifyprice_current",
        "rrp",
        "sales_30d",
        "sales_90d",
        "sales_velocity_per_day",
        "days_of_stock_left",
        "recommended_restock_qty"
    ]

    if not st.session_state.filtered_df.empty:
        st.dataframe(st.session_state.filtered_df[columns_to_show], use_container_width=True)
    else:
        st.warning("No data matches your current filters.")

except Exception as e:
    st.error(f"Error loading data: {e}")
