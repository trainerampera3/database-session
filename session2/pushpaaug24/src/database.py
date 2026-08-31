import psycopg


def create_connection():

    return psycopg.connect(
        host="localhost",
        port="5433",
        dbname="Hotels_db",
        user="pushpa",
        password="pushpa"
    )