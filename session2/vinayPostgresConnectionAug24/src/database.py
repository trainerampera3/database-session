import psycopg


def get_connection():
    return psycopg.connect(
        host="localhost",
        port=5432,
        user="vinay",
        dbname="UsedCarsDataBase",
        password="admin@123"
    )