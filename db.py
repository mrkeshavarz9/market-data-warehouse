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


