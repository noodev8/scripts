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

def apply_price_change(current_price_str, change_type):
    """Apply percentage change to price string"""
    try:
        current_price = float(str(current_price_str).replace('£', '').replace(',', ''))
        multipliers = {
            'increase_2': 1.02,
            'increase_5': 1.05,
            'increase_10': 1.10,
            'decrease_2': 0.98,
            'decrease_5': 0.95,
            'decrease_10': 0.90
        }
        new_price = current_price * multipliers.get(change_type, 1.0)
        return round(new_price, 2)
    except:
        return None

try:
    df = query_health_check()

    # Initialize session state
    if 'filtered_df' not in st.session_state:
        st.session_state.filtered_df = df.sort_values('annual_profit', ascending=False) if 'annual_profit' in df.columns else df
    if 'filter_applied' not in st.session_state:
        st.session_state.filter_applied = False
    if 'selected_rows' not in st.session_state:
        st.session_state.selected_rows = set()
    if 'price_changes' not in st.session_state:
        st.session_state.price_changes = {}
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 1
    if 'include_text' not in st.session_state:
        st.session_state.include_text = ""
    if 'exclude_text' not in st.session_state:
        st.session_state.exclude_text = ""

    # Filter form
    with st.container():
        with st.form(key="filter_form"):
            col1, col2, col3, col4 = st.columns([3, 3, 1.5, 1.5])
            with col1:
                include_text = st.text_input("Include:", value=st.session_state.include_text, help="Search in code, brand, owner, status, segment, recommended_action, title")
            with col2:
                exclude_text = st.text_input("Exclude:", value=st.session_state.exclude_text, help="Search in code, brand, owner, status, segment, recommended_action, title")
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                filter_clicked = st.form_submit_button("🔍 Filter", use_container_width=True)
            with col4:
                st.markdown("<br>", unsafe_allow_html=True)
                reset_clicked = st.form_submit_button("🔄 Reset", use_container_width=True)

    # Handle filtering
    if filter_clicked:
        current_df = st.session_state.filtered_df if st.session_state.filter_applied else df
        filtered_result = filter_dataframe(current_df, include_text, exclude_text)
        st.session_state.filtered_df = filtered_result.sort_values('annual_profit', ascending=False) if 'annual_profit' in filtered_result.columns else filtered_result
        st.session_state.filter_applied = True
        st.session_state.selected_rows = set()  # Clear selections on new filter
        st.session_state.page_number = 1
        # Clear the text fields for next use
        st.session_state.include_text = ""
        st.session_state.exclude_text = ""
        # Show success message with filter details
        filter_terms = []
        if include_text.strip():
            filter_terms.append(f"including '{include_text}'")
        if exclude_text.strip():
            filter_terms.append(f"excluding '{exclude_text}'")
        if filter_terms:
            st.success(f"✅ Filtered data {' and '.join(filter_terms)} - found {len(filtered_result)} items")
        st.rerun()

    if reset_clicked:
        st.session_state.filtered_df = df.sort_values('annual_profit', ascending=False) if 'annual_profit' in df.columns else df
        st.session_state.filter_applied = False
        st.session_state.selected_rows = set()
        st.session_state.price_changes = {}
        st.session_state.page_number = 1
        # Clear the text fields
        st.session_state.include_text = ""
        st.session_state.exclude_text = ""

    # Display stats
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
        gb.configure_selection(selection_mode='multiple', use_checkbox=True)
        gb.configure_grid_options(rowSelection='multiple')

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

        # Display grid with dynamic key to force refresh after removals
        grid_key = f'main_grid_{st.session_state.page_number}_{len(st.session_state.filtered_df)}'
        grid_response = AgGrid(
            display_data,
            gridOptions=grid_options,
            data_return_mode=DataReturnMode.AS_INPUT,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            fit_columns_on_grid_load=False,
            enable_enterprise_modules=False,
            height=calculated_height,
            width='100%',
            reload_data=True,  # Force reload after data changes
            key=grid_key
        )

        # Handle grid selection - only update if we actually have valid selections
        try:
            selected_rows = grid_response.get('selected_rows', pd.DataFrame())
            if isinstance(selected_rows, pd.DataFrame) and not selected_rows.empty and 'code' in selected_rows.columns:
                # Verify the selected codes actually exist in our current filtered data
                valid_codes = set(selected_rows['code'].tolist())
                current_codes = set(st.session_state.filtered_df['code'].tolist())
                st.session_state.selected_rows = valid_codes.intersection(current_codes)
            else:
                # No valid selection, ensure we clear it
                if not hasattr(st.session_state, '_clearing_selection'):
                    st.session_state.selected_rows = set()
        except Exception:
            st.session_state.selected_rows = set()

        # Status info - now shows accurate selection count
        if st.session_state.filter_applied:
            st.info(f"Found {len(st.session_state.filtered_df):,} of {len(df):,} rows after filtering | Selected: {len(st.session_state.selected_rows)} rows")
        else:
            st.info(f"Showing all {len(df):,} rows (sorted by annual profit) | Selected: {len(st.session_state.selected_rows)} rows")

        # Selection Management Section - only show if there are actual selections
        if st.session_state.selected_rows and len(st.session_state.selected_rows) > 0:
            st.markdown("---")
            st.subheader("✅ Selected Items Management")
            
            selected_df = df[df['code'].isin(st.session_state.selected_rows)]
            
            # Action buttons in a cleaner layout
            col1, col2, col3 = st.columns([2, 3, 3])
            
            with col1:
                st.markdown("**Remove Items:**")
                if st.button("❌ Remove Selected", key="remove_selected", use_container_width=True):
                    codes_to_remove = st.session_state.selected_rows.copy()
                    st.session_state.filtered_df = st.session_state.filtered_df[
                        ~st.session_state.filtered_df['code'].isin(codes_to_remove)
                    ]
                    # Clear all selection-related state
                    st.session_state.selected_rows = set()
                    st.session_state.price_changes = {}
                    # Clean up temp price values
                    for key in list(st.session_state.keys()):
                        if key.startswith('temp_price_'):
                            del st.session_state[key]
                    st.session_state.page_number = 1
                    st.success(f"✅ Removed {len(codes_to_remove)} items from display")
                    st.rerun()
            
            with col2:
                st.markdown("**Price Increases:**")
                col_inc1, col_inc2, col_inc3 = st.columns(3)
                with col_inc1:
                    if st.button("+2%", key="inc_2", use_container_width=True):
                        for code in st.session_state.selected_rows:
                            item = df[df['code'] == code]
                            if not item.empty:
                                new_price = apply_price_change(item.iloc[0]['shopifyprice_current'], 'increase_2')
                                if new_price:
                                    st.session_state.price_changes[code] = new_price
                        st.rerun()
                with col_inc2:
                    if st.button("+5%", key="inc_5", use_container_width=True):
                        for code in st.session_state.selected_rows:
                            item = df[df['code'] == code]
                            if not item.empty:
                                new_price = apply_price_change(item.iloc[0]['shopifyprice_current'], 'increase_5')
                                if new_price:
                                    st.session_state.price_changes[code] = new_price
                        st.rerun()
                with col_inc3:
                    if st.button("+10%", key="inc_10", use_container_width=True):
                        for code in st.session_state.selected_rows:
                            item = df[df['code'] == code]
                            if not item.empty:
                                new_price = apply_price_change(item.iloc[0]['shopifyprice_current'], 'increase_10')
                                if new_price:
                                    st.session_state.price_changes[code] = new_price
                        st.rerun()
            
            with col3:
                st.markdown("**Price Decreases:**")
                col_dec1, col_dec2, col_dec3 = st.columns(3)
                with col_dec1:
                    if st.button("-2%", key="dec_2", use_container_width=True):
                        for code in st.session_state.selected_rows:
                            item = df[df['code'] == code]
                            if not item.empty:
                                new_price = apply_price_change(item.iloc[0]['shopifyprice_current'], 'decrease_2')
                                if new_price:
                                    st.session_state.price_changes[code] = new_price
                        st.rerun()
                with col_dec2:
                    if st.button("-5%", key="dec_5", use_container_width=True):
                        for code in st.session_state.selected_rows:
                            item = df[df['code'] == code]
                            if not item.empty:
                                new_price = apply_price_change(item.iloc[0]['shopifyprice_current'], 'decrease_5')
                                if new_price:
                                    st.session_state.price_changes[code] = new_price
                        st.rerun()
                with col_dec3:
                    if st.button("-10%", key="dec_10", use_container_width=True):
                        for code in st.session_state.selected_rows:
                            item = df[df['code'] == code]
                            if not item.empty:
                                new_price = apply_price_change(item.iloc[0]['shopifyprice_current'], 'decrease_10')
                                if new_price:
                                    st.session_state.price_changes[code] = new_price
                        st.rerun()

            # Manual price editing section
            st.markdown("---")
            st.markdown("**Manual Price Editing:**")
            
            # Create a form for manual price inputs to avoid constant reruns
            with st.form("price_editing_form"):
                for idx, row in selected_df.iterrows():
                    code = row['code']
                    current_price_str = str(row['shopifyprice_current']).replace('£', '').replace(',', '')
                    
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                    with col1:
                        st.text(f"Code: {code}")
                    with col2:
                        st.text(f"Brand: {row['brand']}")
                    with col3:
                        st.text(f"Current: £{current_price_str}")
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
                        
                        # Store the price for processing when form is submitted
                        st.session_state[f"temp_price_{code}"] = new_price
                
                # Submit button for manual changes
                if st.form_submit_button("💾 Update Manual Prices", use_container_width=True):
                    for code in st.session_state.selected_rows:
                        temp_price_key = f"temp_price_{code}"
                        if temp_price_key in st.session_state:
                            new_price = st.session_state[temp_price_key]
                            # Get original price
                            item = df[df['code'] == code]
                            if not item.empty:
                                current_price_str = str(item.iloc[0]['shopifyprice_current']).replace('£', '').replace(',', '')
                                try:
                                    original_price = float(current_price_str)
                                    if abs(new_price - original_price) > 0.01:
                                        st.session_state.price_changes[code] = new_price
                                    elif code in st.session_state.price_changes:
                                        del st.session_state.price_changes[code]
                                except:
                                    pass
                    st.rerun()

            # Price changes summary and confirmation
            if st.session_state.price_changes:
                st.markdown("---")
                st.markdown("**📋 Price Changes Summary:**")
                
                changes_summary = []
                for code, new_price in st.session_state.price_changes.items():
                    item_row = df[df['code'] == code]
                    if not item_row.empty:
                        current_price_str = str(item_row.iloc[0]['shopifyprice_current']).replace('£', '').replace(',', '')
                        try:
                            current_price = float(current_price_str)
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
                    col_confirm1, col_confirm2 = st.columns([1, 1])
                    with col_confirm1:
                        if st.button("✅ Confirm All Price Changes", key="confirm_changes", type="primary", use_container_width=True):
                            st.success(f"✅ Price changes confirmed for {len(changes_summary)} items!")
                            st.info("💡 Ready for implementation - these changes will be applied to your system")
                            # TODO: Implement actual price update logic here
                    
                    with col_confirm2:
                        if st.button("🔄 Clear All Changes", key="clear_changes", use_container_width=True):
                            st.session_state.price_changes = {}
                            # Clean up temp price values
                            for key in list(st.session_state.keys()):
                                if key.startswith('temp_price_'):
                                    del st.session_state[key]
                            st.rerun()

    else:
        st.warning("No data matches your current filters.")

except Exception as e:
    st.error(f"Error loading data: {e}")