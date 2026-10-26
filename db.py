import os
from dotenv import load_dotenv
import psycopg2

def get_connection():
    load_dotenv()
    password = os.environ.get("POSTGRES_PASSWORD")
    if password is None:
        raise ValueError("POSTGRES_PASSWORD in .env file is missing!!!")

    conn = psycopg2.connect(
    host="localhost",
    port="5432",
    dbname="market_data",
    user="market_admin",
    password=password
    )
    
    return conn

def create_tables(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS assets(
    asset_id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100),
    asset_type VARCHAR(20) NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS daily_prices(
    price_id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(asset_id),
    date DATE NOT NULL,
    close_price NUMERIC(12, 4),
    volume BIGINT,
    UNIQUE (asset_id, date)
    )
    """)
    



