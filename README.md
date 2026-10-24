# Market Data Warehouse

A small data warehouse in PostgreSQL that stores daily market prices for stocks and crypto.
The first pipeline extracts daily AAPL prices from the Alpha Vantage API and loads them into PostgreSQL.

## Tech Stack

- Python (requests, psycopg2, python-dotenv)
- PostgreSQL 15 running in Docker (Docker Compose)
- Git and GitHub

## Database Design

Two tables, linked by a foreign key:

- `assets`: one row per asset (`asset_id`, `symbol`, `name`, `asset_type`). `symbol` is unique.
- `daily_prices`: one row per asset per day (`asset_id`, `date`, `close_price`, `volume`).
  `(asset_id, date)` is unique, so the same day is never stored twice.

## How the Pipeline Works (`aapl_etl.py`)

1. Load secrets from `.env` and stop early with a clear error if any are missing
2. **Extract:** request the last 100 days of AAPL prices from Alpha Vantage
3. Stop early with the API's own message if no price data was returned
4. Connect to PostgreSQL and create the tables if they do not exist
5. Register AAPL in `assets` if needed, then look up its `asset_id`
6. **Transform:** build one row per day: `(asset_id, date, close_price, volume)`
7. **Load:** insert rows with `ON CONFLICT DO NOTHING`, so running the script again is safe (idempotent)
8. Report how many rows were actually added, commit, and close the connection

## How to Run

1. Clone the repository
2. Create a `.env` file from the template and fill in your own values: `cp .env.example .env` (Windows PowerShell: `Copy-Item .env.example .env`)
3. Start PostgreSQL: `docker compose up -d`
4. Install the Python packages: `pip install requests psycopg2-binary python-dotenv`
5. Run the pipeline: `python aapl_etl.py`

python aapl_etl.py

## Next Steps

- Add a separate pipeline for Bitcoin (CoinGecko API)
- Use upsert (`ON CONFLICT DO UPDATE`) to correct incomplete data for the current day
- Refactor the script into functions and add error handling
- Schedule the pipelines with Apache Airflow
- Add tests with pytest