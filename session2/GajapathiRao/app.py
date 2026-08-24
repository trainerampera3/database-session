from pathlib import Path
import psycopg


BASE_DIR = Path(__file__).resolve().parent
SCHEMA_FILE = BASE_DIR / "sql" / "schema.sql"


def create_connection():
    try:
        connection = psycopg.connect(
            host="localhost",
            dbname="postgres",
            user="gajapathi",
            password="admin@123"
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

if connection:
    create_schema(connection)
    connection.close()