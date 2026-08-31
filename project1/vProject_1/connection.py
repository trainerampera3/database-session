import psycopg

def get_connection():
    connection = psycopg.connect(
        dbname="business_location_intelligence_db",
        user="vinay",
        password="admin@123",
        host="localhost",
        port="5432"
    )
    return connection
