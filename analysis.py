import pandas as pd
from db import get_engine

engine = get_engine()

query = ("""
SELECT symbol,
    count (*) as days_count
FROM assets
JOIN daily_prices ON assets.asset_id = daily_prices.asset_id
GROUP BY symbol
""")

result = pd.read_sql(query, engine)
print(result)