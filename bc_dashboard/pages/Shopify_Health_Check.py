import streamlit as st
from db_utils import query_health_check

st.set_page_config(
    page_title="Shopify Health Check",
    page_icon="✅",
    layout="wide"
)

st.title("✅ Shopify Health Check")
st.subheader("Code Level Stock and Price Management")

# st.info("Connecting to database and loading data...")

try:
    df = query_health_check()
    st.success(f"Loaded {len(df):,} rows from PostgreSQL.")

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
    st.dataframe(df[columns_to_show], use_container_width=True)

    # st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"Error loading data: {e}")
