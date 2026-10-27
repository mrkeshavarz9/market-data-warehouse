# 1. Import libraries
import requests
import pandas as pd
from db import get_connection, create_tables, get_asset_id, count_rows

# 2. Load .env and read password

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
conn = get_connection()
cur = conn.cursor()
print("connected successfully!")

# 5. Create tables if they do not exist
try:
    create_tables(cur)

# 6. Get asset_id for bitcoin from the assets table
    asset_id = get_asset_id(cur, "bitcoin", "bitcoin", "crypto")

    count_before = count_rows(cur, asset_id)
    print(f"number of rows before adding is: {count_before}")
    print(f"asset_id for bitcoin: {asset_id}")

# 7. Transform: build a list of tuples (asset_id, date, close_price, volume)
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

    count_after = count_rows(cur, asset_id)
    print(f"number of rows after adding is: {count_after}")
    print(f"So, difference between before adding and after adding is: {count_after - count_before}")

# 9. Commit the transaction
    conn.commit()
    print("Bitcoin pipeline finished successfully")

except Exception as e:
    conn.rollback()
    print(f"Bitcoin pipeline failed: {e}")
    raise

# 10. Close the cursor and the connection

finally:
    cur.close()
    conn.close()