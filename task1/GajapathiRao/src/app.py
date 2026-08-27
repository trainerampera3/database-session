import os
from dotenv import load_dotenv
import psycopg

load_dotenv()



def create_connection():
    try:
        connection = psycopg.connect(
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
    
def create_schema(connection):

    print("Schema file:", SCHEMA_FILE)

    schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")

    with connection.cursor() as cursor:
        cursor.execute(schema_sql)

    connection.commit()

    print("Schema created successfully.")


connection = create_connection()

create_schema(connection)