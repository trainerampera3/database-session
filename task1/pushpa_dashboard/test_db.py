from db import get_connection

conn = get_connection()

print("PostgreSQL connection successful.")

conn.close()