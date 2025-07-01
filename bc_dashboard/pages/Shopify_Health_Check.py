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
    search_columns = ['code', 'brand', 'owner', 'status', 'segment']
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
    df = query_health_check()

    if 'filtered_df' not in st.session_state:
        st.session_state.filtered_df = df.sort_values('annual_profit', ascending=False) if 'annual_profit' in df.columns else df
    if 'filter_applied' not in st.session_state:
        st.session_state.filter_applied = False
    if 'selected_rows' not in st.session_state:
        st.session_state.selected_rows = set()
    if 'last_filter_state' not in st.session_state:
        st.session_state.last_filter_state = ""

    with st.container():
        with st.form(key="filter_form", clear_on_submit=True):
            col1, col2, col3, col4 = st.columns([3, 3, 1.5, 1.5])
            with col1:
                include_text = st.text_input("Include:", help="Search in code, brand, owner, status, segment, title")
            with col2:
                exclude_text = st.text_input("Exclude:", help="Search in code, brand, owner, status, segment, title")
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                filter_clicked = st.form_submit_button("🔍 Filter", use_container_width=True)
            with col4:
                st.markdown("<br>", unsafe_allow_html=True)
                reset_clicked = st.form_submit_button("🔄 Reset", use_container_width=True)

    current_filter_state = f"{include_text}|{exclude_text}"
    if current_filter_state != st.session_state.last_filter_state:
        st.session_state.selected_rows = set()
        st.session_state.last_filter_state = current_filter_state

    if filter_clicked or (include_text.strip() or exclude_text.strip()):
        current_df = st.session_state.filtered_df if st.session_state.filter_applied else df
        filtered_result = filter_dataframe(current_df, include_text, exclude_text)
        st.session_state.filtered_df = filtered_result.sort_values('annual_profit', ascending=False) if 'annual_profit' in filtered_result.columns else filtered_result
        st.session_state.filter_applied = True

    if reset_clicked:
        st.session_state.filtered_df = df.sort_values('annual_profit', ascending=False) if 'annual_profit' in df.columns else df
        st.session_state.filter_applied = False
        st.session_state.selected_rows = set()

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

    # This will be updated after the grid selection is processed
    if st.session_state.filter_applied:
        st.info(f"Found {len(st.session_state.filtered_df):,} of {len(df):,} rows after filtering | Selected: {len(st.session_state.selected_rows) if st.session_state.selected_rows else 0} rows")
    else:
        st.info(f"Showing all {len(df):,} rows (sorted by annual profit) | Selected: {len(st.session_state.selected_rows) if st.session_state.selected_rows else 0} rows")

    st.markdown("---")

    if 'page_number' not in st.session_state:
        st.session_state.page_number = 1

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

        # Format currency columns for better display
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

        # Configure AgGrid options
        gb = GridOptionsBuilder.from_dataframe(display_data)

        # Enable checkbox selection with simpler configuration
        gb.configure_selection(
            selection_mode='multiple',
            use_checkbox=True
        )

        # Enable row selection
        gb.configure_grid_options(rowSelection='multiple')

        # Configure columns for better display with alignment
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
        gb.configure_column("notes", headerName="Notes", width=200)  # Left aligned as requested
        gb.configure_column("sold_qty", headerName="Sold Qty", width=100, cellStyle={'textAlign': 'center'})

        # Build grid options
        grid_options = gb.build()

        # Calculate height for all rows
        approx_row_height = 36
        header_height = 40
        calculated_height = len(display_data) * approx_row_height + header_height

        # Display AgGrid
        grid_response = AgGrid(
            display_data,
            gridOptions=grid_options,
            data_return_mode=DataReturnMode.AS_INPUT,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            fit_columns_on_grid_load=False,
            enable_enterprise_modules=False,
            height=calculated_height,
            width='100%',
            reload_data=False,
            key='main_grid'  # Add unique key
        )

        # Handle selection safely
        try:
            selected_rows = grid_response.get('selected_rows', pd.DataFrame())

            # Check if we have selections
            if isinstance(selected_rows, pd.DataFrame) and not selected_rows.empty:
                st.write(f"DEBUG: selected_df columns: {list(selected_rows.columns)}")
                if 'code' in selected_rows.columns:
                    selected_codes = selected_rows['code'].tolist()
                    st.write(f"DEBUG: selected_codes: {selected_codes}")
                    # Store the codes in session state
                    st.session_state.selected_rows = set(selected_codes)
                else:
                    st.session_state.selected_rows = set()
            else:
                # Clear selections if nothing selected
                st.session_state.selected_rows = set()

        except Exception as e:
            # Handle any selection errors gracefully
            st.warning(f"Selection error: {e}")
            st.session_state.selected_rows = set()

        if st.session_state.selected_rows:
            st.subheader("✅ Selected Items & Price Management")
            selected_df = df[df['code'].isin(st.session_state.selected_rows)]

            # Price management controls
            col_actions1, col_actions2, col_actions3 = st.columns([2, 2, 2])

            with col_actions1:
                st.markdown("**Bulk Actions:**")
                if st.button("❌ Remove Selected from Display", key="remove_selected"):
                    # Remove selected items from current filtered view
                    codes_to_remove = st.session_state.selected_rows.copy()
                    st.session_state.filtered_df = st.session_state.filtered_df[
                        ~st.session_state.filtered_df['code'].isin(codes_to_remove)
                    ]
                    st.session_state.selected_rows = set()  # Clear selections
                    st.session_state.price_changes = {}  # Clear any price changes
                    # Reset to page 1 if current page would be empty
                    st.session_state.page_number = 1
                    st.rerun()

            with col_actions2:
                st.markdown("**Price Increases:**")
                col_inc1, col_inc2, col_inc3 = st.columns(3)
                with col_inc1:
                    if st.button("+2%", key="inc_2"):
                        st.session_state.price_action = "increase_2"
                        st.rerun()
                with col_inc2:
                    if st.button("+5%", key="inc_5"):
                        st.session_state.price_action = "increase_5"
                        st.rerun()
                with col_inc3:
                    if st.button("+10%", key="inc_10"):
                        st.session_state.price_action = "increase_10"
                        st.rerun()

            with col_actions3:
                st.markdown("**Price Decreases:**")
                col_dec1, col_dec2, col_dec3 = st.columns(3)
                with col_dec1:
                    if st.button("-2%", key="dec_2"):
                        st.session_state.price_action = "decrease_2"
                        st.rerun()
                with col_dec2:
                    if st.button("-5%", key="dec_5"):
                        st.session_state.price_action = "decrease_5"
                        st.rerun()
                with col_dec3:
                    if st.button("-10%", key="dec_10"):
                        st.session_state.price_action = "decrease_10"
                        st.rerun()

            # Display selected items with editable prices
            st.markdown("---")
            st.markdown("**Selected Items (click prices to edit manually):**")

            # Initialize price changes session state
            if 'price_changes' not in st.session_state:
                st.session_state.price_changes = {}

            # Create editable dataframe for selected items
            selected_display = selected_df[columns_to_show].copy()

            # Add current price and new price columns
            selected_display['current_price'] = selected_display['shopifyprice_current']
            selected_display['new_price'] = selected_display['shopifyprice_current']

            # Apply any bulk price changes
            if hasattr(st.session_state, 'price_action'):
                action = st.session_state.price_action
                for idx in selected_display.index:
                    code = selected_display.loc[idx, 'code']
                    current_price_str = str(selected_display.loc[idx, 'current_price'])

                    # Extract numeric value from price string (remove £ and commas)
                    try:
                        current_price = float(current_price_str.replace('£', '').replace(',', ''))

                        if action == "increase_2":
                            new_price = current_price * 1.02
                        elif action == "increase_5":
                            new_price = current_price * 1.05
                        elif action == "increase_10":
                            new_price = current_price * 1.10
                        elif action == "decrease_2":
                            new_price = current_price * 0.98
                        elif action == "decrease_5":
                            new_price = current_price * 0.95
                        elif action == "decrease_10":
                            new_price = current_price * 0.90
                        else:
                            new_price = current_price

                        # Store the price change
                        st.session_state.price_changes[code] = round(new_price, 2)
                        selected_display.loc[idx, 'new_price'] = f"£{new_price:.2f}"
                    except:
                        pass

                # Clear the action after applying
                del st.session_state.price_action

            # Apply any stored price changes
            for code, new_price in st.session_state.price_changes.items():
                if code in selected_display['code'].values:
                    idx = selected_display[selected_display['code'] == code].index[0]
                    selected_display.loc[idx, 'new_price'] = f"£{new_price:.2f}"

            # Show manual price editing section
            st.markdown("**Manual Price Editing:**")

            # Create individual price inputs for each selected item
            for idx, row in selected_display.iterrows():
                code = row['code']
                current_price_str = str(row['current_price']).replace('£', '').replace(',', '')

                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                with col1:
                    st.text(f"Code: {code}")
                with col2:
                    st.text(f"Brand: {row['brand']}")
                with col3:
                    st.text(f"Current: {row['current_price']}")
                with col4:
                    # Get current new price or default to current price
                    current_new_price = st.session_state.price_changes.get(code, None)
                    if current_new_price is None:
                        try:
                            current_new_price = float(current_price_str)
                        except:
                            current_new_price = 0.0

                    new_price = st.number_input(
                        "New Price",
                        value=current_new_price,
                        min_value=0.01,
                        step=0.01,
                        format="%.2f",
                        key=f"price_input_{code}",
                        label_visibility="collapsed"
                    )

                    # Store the price change if different from current
                    try:
                        original_price = float(current_price_str)
                        if abs(new_price - original_price) > 0.01:  # Only store if changed
                            st.session_state.price_changes[code] = new_price
                        elif code in st.session_state.price_changes and abs(new_price - original_price) <= 0.01:
                            # Remove from changes if set back to original
                            del st.session_state.price_changes[code]
                    except:
                        pass

            # Price change confirmation section
            if st.session_state.price_changes:
                st.markdown("---")
                st.markdown("**📋 Price Changes Summary:**")

                changes_summary = []
                for code, new_price in st.session_state.price_changes.items():
                    item_row = selected_df[selected_df['code'] == code]
                    if not item_row.empty:
                        current_price_str = str(item_row.iloc[0]['shopifyprice_current'])
                        try:
                            current_price = float(current_price_str.replace('£', '').replace(',', ''))
                            change_pct = ((new_price - current_price) / current_price) * 100
                            changes_summary.append({
                                'Code': code,
                                'Brand': item_row.iloc[0]['brand'],
                                'Current Price': f"£{current_price:.2f}",
                                'New Price': f"£{new_price:.2f}",
                                'Change': f"{change_pct:+.1f}%"
                            })
                        except:
                            pass

                if changes_summary:
                    changes_df = pd.DataFrame(changes_summary)
                    st.dataframe(changes_df, use_container_width=True, hide_index=True)

                    # Confirmation buttons
                    col_confirm1, col_confirm2, col_confirm3 = st.columns([2, 2, 6])
                    with col_confirm1:
                        if st.button("✅ Confirm Price Changes", key="confirm_changes", type="primary"):
                            st.success(f"Price changes confirmed for {len(changes_summary)} items!")
                            st.info("Implementation: This will update prices in your system")
                            # TODO: Implement actual price update logic here

                    with col_confirm2:
                        if st.button("🔄 Clear All Changes", key="clear_changes"):
                            st.session_state.price_changes = {}
                            st.rerun()



    else:
        st.warning("No data matches your current filters.")

except Exception as e:
    st.error(f"Error loading data: {e}")
