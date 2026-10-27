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

query = ("""
SELECT x,
    RANK()       OVER (ORDER BY x DESC) AS rnk,
    DENSE_RANK() OVER (ORDER BY x DESC) AS dense_rnk,
    ROW_NUMBER() OVER (ORDER BY x DESC) AS row_num
FROM (VALUES (10), (10), (8)) AS t(x)
""")

result = pd.read_sql(query, engine)
print(result)

ma7_query = ("""
SELECT 
    symbol,
    date,
    close_price,
    ROUND(AVG(close_price) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS ma_7
FROM assets
JOIN daily_prices ON assets.asset_id = daily_prices.asset_id
ORDER BY symbol, date DESC
""")

ma7_result = pd.read_sql(ma7_query, engine)
print(ma7_result)