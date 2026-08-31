import psycopg

conn = psycopg.connect(
    host="localhost",
    port="5433",
    dbname="services",
    user="pushpa",
    password="pushpa"
)

cur = conn.cursor()

cur.execute("DELETE FROM bookings")
print("All existing data deleted successfully")
cur.execute("DELETE FROM customers")
print("All existing data deleted successfully")
cur.execute("DELETE FROM hotels")
print("All existing data deleted successfully")

conn.commit()

print("All existing data deleted successfully")

cur.close()
conn.close()