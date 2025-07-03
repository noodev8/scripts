import os
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
from sqlalchemy import create_engine

# Load .env variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Build SQLAlchemy connection string
def get_sqlalchemy_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")

    connection_string = (
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    )
    return create_engine(connection_string)

# Cached query
@st.cache_data
def query_health_check():
    engine = get_sqlalchemy_engine()
    sql = "SELECT * FROM shopify_health_check"
    df = pd.read_sql(sql, engine)
    return df

# Cached query for home page statistics
@st.cache_data
def query_home_stats():
    engine = get_sqlalchemy_engine()
    sql = """
    SELECT
        COUNT(*) as total_skus,
        COUNT(CASE WHEN annual_profit >= 100 THEN 1 END) as skus_100_plus,
        COUNT(CASE WHEN segment = 'Winner' THEN 1 END) as winners,
        COUNT(CASE WHEN segment = 'Loser' THEN 1 END) as losers,
        COUNT(CASE WHEN recommended_action != 'OK' THEN 1 END) as needs_attention,
        COUNT(CASE WHEN local_stock < 5 THEN 1 END) as low_stock,
        COUNT(CASE WHEN sales_30d = 0 THEN 1 END) as no_sales_30d,
        COUNT(CASE WHEN sales_90d = 0 THEN 1 END) as no_sales_90d,
        SUM(local_stock) as total_local_stock,
        AVG(CASE WHEN sales_velocity_per_day > 0 THEN sales_velocity_per_day END) as avg_sales_velocity
    FROM shopify_health_check
    """
    df = pd.read_sql(sql, engine)
    return df.iloc[0]  # Return first row as Series

# Cached query for top performers by annual profit
@st.cache_data
def query_top_performers():
    engine = get_sqlalchemy_engine()
    sql = """
    SELECT
        code,
        brand,
        segment,
        sales_30d,
        sales_velocity_per_day,
        annual_profit,
        local_stock,
        recommended_action
    FROM shopify_health_check
    ORDER BY annual_profit DESC
    LIMIT 10
    """
    df = pd.read_sql(sql, engine)
    return df

# Cached query for items needing attention
@st.cache_data
def query_attention_items():
    engine = get_sqlalchemy_engine()
    sql = """
    SELECT
        code,
        brand,
        segment,
        recommended_action,
        total_stock,
        sales_30d,
        annual_profit
    FROM shopify_health_check
    WHERE recommended_action != 'OK'
    ORDER BY
        CASE recommended_action
            WHEN 'Restock' THEN 1
            WHEN 'Price Too Low' THEN 2
            WHEN 'Price Too High' THEN 3
            WHEN 'Stock Not Moving' THEN 4
            WHEN 'Clearance' THEN 5
            WHEN 'Discontinue' THEN 6
            ELSE 7
        END,
        annual_profit DESC
    LIMIT 15
    """
    df = pd.read_sql(sql, engine)
    return df
