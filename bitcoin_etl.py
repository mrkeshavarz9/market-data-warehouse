# 1. Import libraries
import os
from dotenv import load_dotenv
import requests
import psycopg2
import pandas as pd

# 2. Load .env and read password
load_dotenv()
password = os.environ.get("POSTGRES_PASSWORD")
if password is None:
    raise ValueError("POSTGRES_PASSWORD in .env file is missing!!!")

# 3. Extract: request daily bitcoin prices from CoinGecko
url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
params = {
    "vs_currency": "usd",
    "days" : 100
}
response = requests.get(url, params=params)
btc_data = response.json()
if "prices" not in btc_data:
    raise ValueError(f"CoinGecko returned no prices. Responses: {btc_data}")
if "total_volumes" not in btc_data:
    raise ValueError(f"CoinGecko returned no total volumes. Responses: {btc_data}")

prices = btc_data["prices"]
total_volumes = btc_data["total_volumes"]
total_vilumes = btc_data["total_volumes"]
print(f"{len(prices)} days received for bitcoin")

# 4. Connect to PostgreSQL and create a cursor
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    dbname="market_data",
    user="market_admin",
    password=password
)
cur = conn.cursor()
print("connected successfully!")

# 5. Create tables if they do not exist
cur.execute ("""
CREATE TABLE IF NOT EXISTS assets(
asset_id SERIAL PRIMARY KEY,
symbol VARCHAR(20) NOT NULL UNIQUE,
name VARCHAR(100),
asset_type VARCHAR(20) NOT NULL
)
""")

cur.execute ("""
CREATE TABLE IF NOT EXISTS daily_prices(
price_id SERIAL PRIMARY KEY,
asset_id INTEGER REFERENCES assets(asset_id),
date DATE NOT NULL,
close_price NUMERIC(12, 4),
volume BIGINT,
UNIQUE (asset_id, date)
)
""")

# 6. Get asset_id for bitcoin from the assets table
cur.execute("""
INSERT INTO assets (symbol, name, asset_type)
VALUES
    (%s, %s, %s)
ON CONFLICT (symbol) DO NOTHING
""", ('bitcoin', 'bitcoin', 'crypto'))

cur.execute (" SELECT asset_id FROM assets WHERE symbol = %s", ("bitcoin",))
row = cur.fetchone()
if row is None:
    raise ValueError("we didnt find bitcoin in assets")
asset_id = row[0]

cur.execute("SELECT COUNT(*) FROM daily_prices WHERE asset_id = %s", (asset_id,))
count_before = cur.fetchone()[0]
print(f"number of rows before adding is: {count_before}")

print(f"asset_id for bitcoin: {asset_id}")

# 7. Transform: build a list of tuples (asset_id, date, close_price, volume)
timestamp = prices[0][0]
timestamp = pd.to_datetime(timestamp, unit="ms").date()

rows = []
for p, v in zip(prices, total_volumes):
    price_date = p[0]
    price_date = pd.to_datetime(price_date, unit="ms").date() 
    close_price = p[1]
    volume = int(v[1])
    new_record = (asset_id, price_date, close_price, volume)
    rows.append(new_record)
print(f"{len(rows)} rows are ready!")

# 8. Load: insert rows with executemany and ON CONFLICT DO UPDATE SET
cur.executemany("""
INSERT INTO daily_prices (asset_id, date, close_price, volume)
VALUES
    (%s, %s, %s, %s)
ON CONFLICT (asset_id, date) DO UPDATE SET
    close_price = EXCLUDED.close_price,
    volume = EXCLUDED.volume
""",rows)

cur.execute("SELECT COUNT(*) FROM daily_prices WHERE asset_id = %s", (asset_id,))
count_after = cur.fetchone()[0]
print(f"number of rows after adding is: {count_after}")
print(f"So, difference between before adding and after adding is: {count_after - count_before}")

# 9. Commit the transaction
conn.commit()

# 10. Close the cursor and the connection
cur.close()
conn.close()
print("All Done")