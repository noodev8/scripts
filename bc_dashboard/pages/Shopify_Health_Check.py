import streamlit as st
import pandas as pd
from db_utils import query_health_check
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

st.set_page_config(
    page_title="Shopify Health Check",
    page_icon="✅",
    layout="wide"
)

st.title("✅ Shopify Health Check")
st.subheader("Code Level Stock and Price Management")

def filter_dataframe(df, include_text, exclude_text):
    if df.empty:
        return df
    search_columns = ['code', 'brand', 'owner', 'status', 'segment', 'recommended_action']
    if 'title' in df.columns:
        search_columns.append('title')
    filtered_df = df.copy()
    if include_text.strip():
        include_mask = False
        for col in search_columns:
            if col in filtered_df.columns:
                col_mask = filtered_df[col].astype(str).str.lower().str.contains(
                    include_text.lower(), na=False, regex=False
                )
                include_mask = include_mask | col_mask
        filtered_df = filtered_df[include_mask]
    if exclude_text.strip():
        exclude_mask = False
        for col in search_columns:
            if col in filtered_df.columns:
                col_mask = filtered_df[col].astype(str).str.lower().str.contains(
                    exclude_text.lower(), na=False, regex=False
                )
                exclude_mask = exclude_mask | col_mask
        filtered_df = filtered_df[~exclude_mask]
    return filtered_df

def calculate_filter_stats(df):
    if df.empty:
        return {}
    total_items = len(df)
    winners = len(df[df['segment'] == 'Winner']) if 'segment' in df.columns else 0
    winners_percentage = (winners / total_items * 100) if total_items > 0 else 0
    stats = {
        'total_items': total_items,
        'winners': winners,
        'winners_percentage': winners_percentage
    }
    return stats

try:
    df = query_health_check()

    # Initialize session state
    if 'filtered_df' not in st.session_state:
        st.session_state.filtered_df = df.sort_values('annual_profit', ascending=False) if 'annual_profit' in df.columns else df
    if 'filter_applied' not in st.session_state:
        st.session_state.filter_applied = False
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 1
    if 'include_text' not in st.session_state:
        st.session_state.include_text = ""
    if 'exclude_text' not in st.session_state:
        st.session_state.exclude_text = ""
    if 'review_filter' not in st.session_state:
        st.session_state.review_filter = "All"

    # Filter form
    with st.container():
        with st.form(key="filter_form"):
            col1, col2, col3, col4, col5 = st.columns([2.5, 2.5, 2, 1.5, 1.5])
            with col1:
                include_text = st.text_input("Include:", value=st.session_state.include_text, help="Search in code, brand, owner, status, segment, recommended_action, title")
            with col2:
                exclude_text = st.text_input("Exclude:", value=st.session_state.exclude_text, help="Search in code, brand, owner, status, segment, recommended_action, title")
            with col3:
                review_filter = st.selectbox(
                    "Review Status:",
                    options=["All", "Pending (10+ days)", "Current (≤10 days)"],
                    index=["All", "Pending (10+ days)", "Current (≤10 days)"].index(st.session_state.review_filter),
                    help="Filter by review age"
                )
            with col4:
                st.markdown("<br>", unsafe_allow_html=True)
                filter_clicked = st.form_submit_button("🔍 Filter", use_container_width=True)
            with col5:
                st.markdown("<br>", unsafe_allow_html=True)
                reset_clicked = st.form_submit_button("🔄 Reset", use_container_width=True)

    # Handle filtering
    if filter_clicked:
        current_df = df.copy()  # Always start from full dataset

        # Apply review filter
        if review_filter != "All" and 'last_reviewed' in current_df.columns:
            # Convert last_reviewed to datetime, handling various formats
            current_df['last_reviewed_dt'] = pd.to_datetime(current_df['last_reviewed'], errors='coerce')
            # Create timezone-naive comparison date
            ten_days_ago = pd.Timestamp.now().tz_localize(None) - pd.Timedelta(days=10)

            # Make sure both sides are timezone-naive for comparison
            current_df['last_reviewed_dt'] = current_df['last_reviewed_dt'].dt.tz_localize(None)

            if review_filter == "Pending (10+ days)":
                # Show items reviewed more than 10 days ago OR never reviewed (null)
                current_df = current_df[
                    (current_df['last_reviewed_dt'] < ten_days_ago) |
                    (current_df['last_reviewed_dt'].isna())
                ]
            elif review_filter == "Current (≤10 days)":
                # Show items reviewed within the last 10 days
                current_df = current_df[
                    (current_df['last_reviewed_dt'] >= ten_days_ago) &
                    (current_df['last_reviewed_dt'].notna())
                ]

        # Apply text filters
        filtered_result = filter_dataframe(current_df, include_text, exclude_text)

        # Clean up temporary datetime column if it exists
        if 'last_reviewed_dt' in filtered_result.columns:
            filtered_result = filtered_result.drop('last_reviewed_dt', axis=1)

        st.session_state.filtered_df = filtered_result.sort_values('annual_profit', ascending=False) if 'annual_profit' in filtered_result.columns else filtered_result
        st.session_state.filter_applied = True
        st.session_state.review_filter = review_filter
        st.session_state.page_number = 1
        # Clear the text fields for next use
        st.session_state.include_text = ""
        st.session_state.exclude_text = ""
        st.rerun()

    if reset_clicked:
        st.session_state.filtered_df = df.sort_values('annual_profit', ascending=False) if 'annual_profit' in df.columns else df
        st.session_state.filter_applied = False
        st.session_state.review_filter = "All"
        st.session_state.page_number = 1
        # Clear the text fields
        st.session_state.include_text = ""
        st.session_state.exclude_text = ""

    # Display stats
    current_stats = calculate_filter_stats(st.session_state.filtered_df)
    if current_stats:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Items", f"{current_stats['total_items']}")
        with col2:
            st.metric("Winners", f"{current_stats['winners']} ({current_stats['winners_percentage']:.1f}%)")

    st.markdown("---")

    # Pagination
    rows_per_page = 15
    total_rows = len(st.session_state.filtered_df)
    total_pages = max(1, (total_rows + rows_per_page - 1) // rows_per_page)

    if not st.session_state.filtered_df.empty:
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

        # Prepare page data
        start_idx = (st.session_state.page_number - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        page_data = st.session_state.filtered_df.iloc[start_idx:end_idx].copy()

        columns_to_show = [
            "code", "brand", "owner", "status", "segment",
            "annual_profit", "profit_per_unit", "local_stock", "total_stock",
            "shopifyprice_current", "rrp", "sales_30d", "sales_90d",
            "sales_velocity_per_day", "days_of_stock_left", "recommended_action",
            "last_reviewed", "notes", "sold_qty"
        ]
        display_data = page_data[columns_to_show].copy()

        # Format currency columns
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

        st.markdown("<br>", unsafe_allow_html=True)

        # Configure AgGrid
        gb = GridOptionsBuilder.from_dataframe(display_data)

        # Configure columns
        gb.configure_column("code", headerName="Code", width=120, pinned="left")
        gb.configure_column("brand", headerName="Brand", width=140)
        gb.configure_column("owner", headerName="Owner", width=100, cellStyle={'textAlign': 'center'})
        gb.configure_column("status", headerName="Status", width=100, cellStyle={'textAlign': 'center'})
        gb.configure_column("segment", headerName="Segment", width=100, cellStyle={'textAlign': 'center'})
        gb.configure_column("annual_profit", headerName="Annual Profit", width=120, cellStyle={'textAlign': 'right'})
        gb.configure_column("profit_per_unit", headerName="Profit/Unit", width=100, cellStyle={'textAlign': 'right'})
        gb.configure_column("local_stock", headerName="Local Stock", width=100, cellStyle={'textAlign': 'center'})
        gb.configure_column("total_stock", headerName="Total Stock", width=100, cellStyle={'textAlign': 'center'})
        gb.configure_column("shopifyprice_current", headerName="Shopify Price", width=110, cellStyle={'textAlign': 'right'})
        gb.configure_column("rrp", headerName="RRP", width=80, cellStyle={'textAlign': 'right'})
        gb.configure_column("sales_30d", headerName="Sales 30d", width=100, cellStyle={'textAlign': 'center'})
        gb.configure_column("sales_90d", headerName="Sales 90d", width=100, cellStyle={'textAlign': 'center'})
        gb.configure_column("sales_velocity_per_day", headerName="Daily Velocity", width=110, cellStyle={'textAlign': 'center'})
        gb.configure_column("days_of_stock_left", headerName="Days Stock Left", width=120, cellStyle={'textAlign': 'center'})
        gb.configure_column("recommended_action", headerName="Recommended Action", width=150, cellStyle={'textAlign': 'center'})
        gb.configure_column("last_reviewed", headerName="Last Reviewed", width=120, cellStyle={'textAlign': 'center'})
        gb.configure_column("notes", headerName="Notes", width=200)
        gb.configure_column("sold_qty", headerName="Sold Qty", width=100, cellStyle={'textAlign': 'center'})

        grid_options = gb.build()

        # Calculate height
        approx_row_height = 36
        header_height = 40
        calculated_height = len(display_data) * approx_row_height + header_height

        # Display grid
        grid_key = f'main_grid_{st.session_state.page_number}_{len(st.session_state.filtered_df)}'

        grid_response = AgGrid(
            display_data,
            gridOptions=grid_options,
            data_return_mode=DataReturnMode.AS_INPUT,
            update_mode=GridUpdateMode.NO_UPDATE,
            fit_columns_on_grid_load=False,
            enable_enterprise_modules=False,
            height=calculated_height,
            width='100%',
            reload_data=True,
            key=grid_key
        )

        # Download options
        col_download1, col_download2 = st.columns(2)

        with col_download1:
            # Full CSV download for current filtered data
            csv_data = st.session_state.filtered_df.to_csv(index=False)
            st.download_button(
                label="📄 Full Export",
                data=csv_data,
                file_name=f"shopify_health_check_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                help="Download current filtered data as CSV"
            )

        with col_download2:
            # GroupID export - only code and groupid columns
            if 'code' in st.session_state.filtered_df.columns and 'groupid' in st.session_state.filtered_df.columns:
                groupid_data = st.session_state.filtered_df[['code', 'groupid']].to_csv(index=False)
                st.download_button(
                    label="🏷️ GroupID Export",
                    data=groupid_data,
                    file_name=f"groupid_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    help="Download code and groupid only"
                )

    else:
        st.warning("No data matches your current filters.")

except Exception as e:
    st.error(f"Error loading data: {e}")