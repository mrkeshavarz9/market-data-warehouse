# 1. Import libraries
import os
from dotenv import load_dotenv
import requests
from db import get_connection, create_tables

# 2. Load .env and read API key and password
load_dotenv()
api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
if api_key is None:
    raise ValueError("ALPHA_VANTAGE_API_KEY in .env file is missing!!!")

# 3. Extract: request daily AAPL prices from Alpha Vantage
response = requests.get("https://www.alphavantage.co/query", params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": "AAPL",
    "outputsize": "compact",
    "apikey": api_key
})
data = response.json()
if "Time Series (Daily)" not in data:
    raise ValueError(f"Alpha Vantage returned no price data. Responses: {data}")
daily = data["Time Series (Daily)"]
print(f"{len(daily)} days received for AAPL")

# 4. Connect to PostgreSQL and create a cursor
conn = get_connection()
cur = conn.cursor()
print("connected successfully!")

# 5. Create tables if they do not exist
create_tables(cur)

# 6. Get asset_id for AAPL from the assets table
cur.execute("""
INSERT INTO assets (symbol, name, asset_type)
VALUES
    (%s, %s, %s)
ON CONFLICT (symbol) DO NOTHING
""", ('AAPL', 'Apple Inc.', 'stock'))

cur.execute (" SELECT asset_id FROM assets WHERE symbol = %s", ("AAPL",))
row = cur.fetchone()
if row is None:
    raise ValueError("we didnt find AAPL in assets")
asset_id = row[0]

cur.execute("SELECT COUNT(*) FROM daily_prices WHERE asset_id = %s", (asset_id,))
count_before = cur.fetchone()[0]
print(f"number of rows before adding is: {count_before}")

print(f"asset_id for AAPL: {asset_id}")

# 7. Transform: build a list of tuples (asset_id, date, close_price, volume)
rows = []
for date, values in daily.items():
    record = (asset_id, date, values["4. close"], values["5. volume"])
    rows.append(record)
print(f"{len(rows)} rows are ready!")

# 8. Load: insert rows with executemany and ON CONFLICT DO UPDATE SET
cur.executemany("""
INSERT INTO daily_prices (asset_id, date, close_price, volume)
VALUES
    (%s, %s, %s, %s)
ON CONFLICT (asset_id, date) DO UPDATE SET
    close_price = EXCLUDED.close_price,
    volume = EXCLUDED.volume
""", rows)

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