# Market Data Warehouse

A small data warehouse in PostgreSQL that stores daily market prices for stocks and crypto.
It has two independent pipelines: one extracts daily AAPL prices from the Alpha Vantage API, the other extracts daily Bitcoin prices from the CoinGecko API. Both load into the same PostgreSQL database.

## Tech Stack

- Python (requests, psycopg2, python-dotenv, pandas)
- PostgreSQL 15 running in Docker (Docker Compose)
- Git and GitHub

## Database Design

Two tables, linked by a foreign key:

- `assets`: one row per asset (`asset_id`, `symbol`, `name`, `asset_type`). `symbol` is unique.
- `daily_prices`: one row per asset per day (`asset_id`, `date`, `close_price`, `volume`). `(asset_id, date)` is unique, so the same day is never stored twice.

## How the Pipelines Work

Both scripts follow the same steps:

1. Load secrets from `.env` and stop early with a clear error if any are missing
2. **Extract:** request the last 100 days of prices from the API
3. Stop early with the API's own message if the expected data is missing
4. Connect to PostgreSQL and create the tables if they do not exist
5. Register the asset in `assets` if needed, then look up its `asset_id`
6. **Transform:** build one row per day: `(asset_id, date, close_price, volume)`
7. **Load:** insert the rows into `daily_prices`
8. Report how many new rows were added, commit, and close the connection

Differences between the two pipelines:

- `aapl_etl.py` (Alpha Vantage): needs an API key. Only finished trading days are returned, but rows are still inserted with an upsert (`ON CONFLICT DO UPDATE`), so any later corrections from the API are applied instead of ignored.
- `bitcoin_etl.py` (CoinGecko): no API key needed. Prices come as two separate lists (prices and volumes) with Unix timestamps in milliseconds, which are paired with `zip` and converted to dates. Because the crypto market never closes, the current day is always incomplete, so rows are inserted with an upsert (`ON CONFLICT DO UPDATE`): the next run replaces the partial price with the final one.

## How to Run

1. Clone the repository
2. Create a `.env` file from the template and fill in your own values: `cp .env.example .env` (Windows PowerShell: `Copy-Item .env.example .env`)
3. Start PostgreSQL: `docker compose up -d`
4. Install the Python packages: `pip install requests psycopg2-binary python-dotenv pandas`
5. Run the pipelines: `python aapl_etl.py` and `python bitcoin_etl.py`

## Next Steps

- Refactor the scripts into functions and share common code between them
- Add error handling with try/except
- Schedule the pipelines with Apache Airflow
- Add tests with pytest