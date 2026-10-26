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

def get_asset_id(cur, symbol, name, asset_type):
    cur.execute("""
    INSERT INTO assets (symbol, name, asset_type)
    VALUES
        (%s, %s, %s)
    ON CONFLICT (symbol) DO NOTHING
    """, (symbol, name, asset_type))

    cur.execute (" SELECT asset_id FROM assets WHERE symbol = %s", (symbol,))
    row = cur.fetchone()
    if row is None:
        raise ValueError(f"we didnt find {symbol} in assets")
    return row[0]

def count_rows(cur, asset_id):
    cur.execute("SELECT COUNT(*) FROM daily_prices WHERE asset_id = %s", (asset_id,))
    return cur.fetchone()[0]
    


