import os
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
from sqlalchemy import create_engine

# Load .env variables
load_dotenv()

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
