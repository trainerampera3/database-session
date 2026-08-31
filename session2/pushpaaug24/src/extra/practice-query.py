import psycopg

conn = psycopg.connect(
    host="localhost",
    port=5433,
    dbname="services",
    user="pushpa",
    password="pushpa"
)

cur = conn.cursor()

cur.execute("""
   SELECT *
    FROM hotels
    LIMIT 10
 """)
for row in cur.fetchall():
    print(row)

    cur.execute("""
    SELECT *
    FROM bookings
    WHERE adr > 100
    limit 10
""")

for row in cur.fetchall():
    print(row)

cur.execute("""
    SELECT *
    FROM bookings
    ORDER BY adr DESC
    limit 10
""")
cur.execute("""
    SELECT *
    FROM bookings
    WHERE booking_status = 'Canceled'
    limit 10
""")
for row in cur.fetchall():
    print(row)

cur.execute("""
    SELECT
        h.hotel,
        c.country,
        b.arrival_date,
        b.total_nights,
        b.estimated_revenue
    FROM bookings b
    JOIN hotels h
        ON b.hotel_id = h.hotel_id
    JOIN customers c
        ON b.customer_id = c.customer_id
        limit 10
""")

for row in cur.fetchall():
    print(row)

cur.execute("""
    SELECT SUM(estimated_revenue)
    FROM bookings
    limit 10
""")

print(cur.fetchone())

cur.execute("""
    SELECT hotel_id, COUNT(*)
    FROM bookings
    GROUP BY hotel_id
    limit 5
""")

for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
