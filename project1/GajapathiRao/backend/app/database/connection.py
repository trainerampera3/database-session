import psycopg as pg 
from dotenv import load_dotenv
import os

load_dotenv()

def create_connection():
    try:
        connection = pg.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
)

        print("Connection successful.")
        return connection

    except Exception as e:
        print(f"Connection error: {e}")
        return None
    
    
create_connection()