import psycopg as pg 

import os


from dotenv import load_dotenv

load_dotenv()


def create_connection():
    """Create and return a PostgreSQL database connection."""
    try:
        connection = pg.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        print("Database connection established successfully.")
        return connection
    except Exception as exc:  
        print(f"Connection error: {exc}")
        return None

create_connection()