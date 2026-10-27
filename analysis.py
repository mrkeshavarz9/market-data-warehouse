import pandas as pd
from db import get_engine

engine = get_engine()

days_query = ("""
SELECT symbol,
    count (*) as days_count
FROM assets
JOIN daily_prices ON assets.asset_id = daily_prices.asset_id
GROUP BY symbol
""")

days_result = pd.read_sql(days_query, engine)
print(days_result)


top3_query = ("""
WITH ranked AS (
SELECT symbol,
    close_price,
    date,
    RANK() OVER (PARTITION BY symbol ORDER BY close_price DESC) AS price_rank
FROM assets
JOIN daily_prices ON assets.asset_id = daily_prices.asset_id
)
SELECT price_rank,
    date,
    close_price,
    symbol
FROM ranked
WHERE price_rank <= 3
ORDER BY symbol, price_rank
""")

top3_result = pd.read_sql(top3_query, engine)
print(top3_result)