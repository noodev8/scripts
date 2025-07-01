import streamlit as st
import pandas as pd
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

    # Initialize session state for filters and selections
    if 'filtered_df' not in st.session_state:
        # Sort by annual_profit DESC initially
        st.session_state.filtered_df = df.sort_values('annual_profit', ascending=False) if 'annual_profit' in df.columns else df
    if 'filter_applied' not in st.session_state:
        st.session_state.filter_applied = False
    if 'clear_inputs' not in st.session_state:
        st.session_state.clear_inputs = False
    if 'selected_rows' not in st.session_state:
        st.session_state.selected_rows = set()
    if 'last_filter_state' not in st.session_state:
        st.session_state.last_filter_state = ""

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

    # Check if filters have changed (to reset selections)
    current_filter_state = f"{include_text}|{exclude_text}"
    if current_filter_state != st.session_state.last_filter_state:
        st.session_state.selected_rows = set()  # Reset selections when filters change
        st.session_state.last_filter_state = current_filter_state

    # Handle filter button or form submission (Enter/Tab)
    if filter_clicked or (include_text.strip() or exclude_text.strip()):
        # Apply filters to current filtered dataset (progressive filtering)
        current_df = st.session_state.filtered_df if st.session_state.filter_applied else df
        filtered_result = filter_dataframe(current_df, include_text, exclude_text)
        # Sort by annual_profit DESC after filtering
        st.session_state.filtered_df = filtered_result.sort_values('annual_profit', ascending=False) if 'annual_profit' in filtered_result.columns else filtered_result
        st.session_state.filter_applied = True

    # Handle reset button
    if reset_clicked:
        # Sort by annual_profit DESC when resetting
        st.session_state.filtered_df = df.sort_values('annual_profit', ascending=False) if 'annual_profit' in df.columns else df
        st.session_state.filter_applied = False
        st.session_state.selected_rows = set()  # Clear selections on reset

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

    # Show filter results and selection count
    selection_count = len(st.session_state.selected_rows)
    if st.session_state.filter_applied:
        st.info(f"Found {len(st.session_state.filtered_df):,} of {len(df):,} rows after filtering | Selected: {selection_count} rows")
    else:
        st.info(f"Showing all {len(df):,} rows (sorted by annual profit) | Selected: {selection_count} rows")

    st.markdown("---")

    # Pagination setup
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 1

    rows_per_page = 15
    total_rows = len(st.session_state.filtered_df)
    total_pages = max(1, (total_rows + rows_per_page - 1) // rows_per_page)

    if not st.session_state.filtered_df.empty:
        # Pagination controls
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

        with col1:
            if st.button("⏮️ First", disabled=(st.session_state.page_number == 1)):
                st.session_state.page_number = 1
                st.rerun()

        with col2:
            if st.button("◀️ Prev", disabled=(st.session_state.page_number == 1)):
                st.session_state.page_number -= 1
                st.rerun()

        with col3:
            st.markdown(f"<div style='text-align: center; padding: 8px;'><strong>Page {st.session_state.page_number} of {total_pages}</strong><br><small>Showing rows {(st.session_state.page_number-1)*rows_per_page + 1} to {min(st.session_state.page_number*rows_per_page, total_rows)} of {total_rows}</small></div>", unsafe_allow_html=True)

        with col4:
            if st.button("▶️ Next", disabled=(st.session_state.page_number == total_pages)):
                st.session_state.page_number += 1
                st.rerun()

        with col5:
            if st.button("⏭️ Last", disabled=(st.session_state.page_number == total_pages)):
                st.session_state.page_number = total_pages
                st.rerun()

        # Calculate page slice
        start_idx = (st.session_state.page_number - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        page_data = st.session_state.filtered_df.iloc[start_idx:end_idx]

        # Display data for current page
        columns_to_show = [
            "code",
            "brand",
            "owner",
            "status",
            "segment",
            "annual_profit",
            "profit_per_unit",
            "local_stock",
            "total_stock",
            "shopifyprice_current",
            "rrp",
            "sales_30d",
            "sales_90d",
            "sales_velocity_per_day",
            "days_of_stock_left",
            "recommended_action",
            "last_reviewed",
            "notes",
            "sold_qty"
        ]

        # Format the data for better display
        display_data = page_data[columns_to_show].copy()

        # Format currency columns for better readability
        if 'annual_profit' in display_data.columns:
            display_data['annual_profit'] = display_data['annual_profit'].apply(
                lambda x: f"£{x:,.0f}" if pd.notna(x) else "£0"
            )
        if 'profit_per_unit' in display_data.columns:
            display_data['profit_per_unit'] = display_data['profit_per_unit'].apply(
                lambda x: f"£{x:.2f}" if pd.notna(x) else "£0.00"
            )
        if 'shopifyprice_current' in display_data.columns:
            display_data['shopifyprice_current'] = display_data['shopifyprice_current'].apply(
                lambda x: f"£{x}" if pd.notna(x) and str(x).strip() != '' else ""
            )
        if 'rrp' in display_data.columns:
            display_data['rrp'] = display_data['rrp'].apply(
                lambda x: f"£{x}" if pd.notna(x) and str(x).strip() != '' else ""
            )
        if 'sales_velocity_per_day' in display_data.columns:
            display_data['sales_velocity_per_day'] = display_data['sales_velocity_per_day'].apply(
                lambda x: f"{x:.2f}" if pd.notna(x) else "0.00"
            )
        if 'days_of_stock_left' in display_data.columns:
            display_data['days_of_stock_left'] = display_data['days_of_stock_left'].apply(
                lambda x: f"{x:.1f}" if pd.notna(x) else "0.0"
            )

        # Add some spacing before the table
        st.markdown("<br>", unsafe_allow_html=True)

        # Dynamically calculate height based on number of rows
        approx_row_height = 36
        header_height = 40
        calculated_height = len(display_data) * approx_row_height + header_height

        # Display with Streamlit dataframe
        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True,
            height=calculated_height,
            column_config={
                "code": st.column_config.TextColumn("Code", width="medium"),
                "brand": st.column_config.TextColumn("Brand", width="medium"),
                "owner": st.column_config.TextColumn("Owner", width="small"),
                "status": st.column_config.TextColumn("Status", width="small"),
                "segment": st.column_config.TextColumn("Segment", width="small"),
                "annual_profit": st.column_config.TextColumn("Annual Profit", width="small"),
                "profit_per_unit": st.column_config.TextColumn("Profit/Unit", width="small"),
                "local_stock": st.column_config.NumberColumn("Local Stock", width="small"),
                "total_stock": st.column_config.NumberColumn("Total Stock", width="small"),
                "shopifyprice_current": st.column_config.TextColumn("Shopify Price", width="small"),
                "rrp": st.column_config.TextColumn("RRP", width="small"),
                "sales_30d": st.column_config.NumberColumn("Sales 30d", width="small"),
                "sales_90d": st.column_config.NumberColumn("Sales 90d", width="small"),
                "sales_velocity_per_day": st.column_config.TextColumn("Daily Velocity", width="small"),
                "days_of_stock_left": st.column_config.TextColumn("Days Stock Left", width="small"),
                "recommended_action": st.column_config.TextColumn("Recommended Action", width="medium"),
                "last_reviewed": st.column_config.DateColumn("Last Reviewed", width="small"),
                "notes": st.column_config.TextColumn("Notes", width="large"),
                "sold_qty": st.column_config.NumberColumn("Sold Qty", width="small")
            }
        )

        # Reset page number when filters change
        if st.session_state.filter_applied and st.session_state.page_number > total_pages:
            st.session_state.page_number = 1
            st.rerun()

    else:
        st.warning("No data matches your current filters.")

except Exception as e:
    st.error(f"Error loading data: {e}")
