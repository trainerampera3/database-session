from database import create_connection, get_bookings


connection = create_connection()

df = get_bookings(connection)

print(df.head())
print(df.shape)

connection.close()

from database import create_connection, get_kpis


connection = create_connection()

kpis = get_kpis(connection)

print("Total Bookings:", kpis["total_bookings"])
print("Total Guests:", kpis["total_guests"])
print("Total Revenue:", kpis["total_revenue"])
print("Average ADR:", kpis["average_adr"])
print("Cancellation Rate:", kpis["cancellation_rate"])

connection.close()

from database import create_connection
import pandas as pd


connection = create_connection()

query = """
SELECT
    booking_status,
    COUNT(*) AS total
FROM bookings
GROUP BY booking_status
ORDER BY total DESC
"""

df = pd.read_sql_query(query, connection)

print(df)

connection.close()