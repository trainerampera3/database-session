import psycopg

conn= psycopg.connect(
           host="localhost",
          port="5433",
          dbname="Hotels_db",
        user="pushpa", 
        password="pushpa")
print("connection establishged successfully")


cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS hotels (
    hotel_id SERIAL PRIMARY KEY,
    hotel VARCHAR(100) NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    country VARCHAR(10),
    customer_type VARCHAR(50),
    is_repeated_guest INTEGER,
    guest_type VARCHAR(50)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    booking_id SERIAL PRIMARY KEY,
    hotel_id INTEGER REFERENCES hotels(hotel_id),
    customer_id INTEGER REFERENCES customers(customer_id),
    arrival_date DATE,
    total_nights INTEGER,
    total_guests INTEGER,
    meal VARCHAR(20),
    market_segment VARCHAR(50),
    reserved_room_type VARCHAR(10),
    adr NUMERIC(10,2),
    estimated_revenue NUMERIC(12,2),
    booking_status VARCHAR(30)
)
""")

conn.commit()

cur.close()
conn.close()

print("Tables created successfully")