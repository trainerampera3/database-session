# import csv
# import psycopg

# conn= psycopg.connect(
#            host="localhost",
#           port="5433",
#           dbname="services",
#         user="pushpa", 
#         password="pushpa")

# cur = conn.cursor()

# with open("data/hotel_bookings_cleaned.csv", "r", encoding="utf-8") as file:

#     reader = csv.DictReader(file)

#     for row in reader:

#         cur.execute(
#             """
#             INSERT INTO hotels (hotel)
#             VALUES (%s)
#             RETURNING hotel_id
#             """,
#             (row["hotel"],)
#         )

#         hotel_id = cur.fetchone()[0]

#         cur.execute(
#             """
#             INSERT INTO customers
#             (country, customer_type, is_repeated_guest, guest_type)
#             VALUES (%s, %s, %s, %s)
#             RETURNING customer_id
#             """,
#             (
#                 row["country"],
#                 row["customer_type"],
#                 row["is_repeated_guest"],
#                 row["guest_type"]
#             )
#         )

#         customer_id = cur.fetchone()[0]

#         cur.execute(
#             """
#             INSERT INTO bookings
#             (
#                 hotel_id,
#                 customer_id,
#                 arrival_date,
#                 total_nights,
#                 total_guests,
#                 meal,
#                 market_segment,
#                 reserved_room_type,
#                 adr,
#                 estimated_revenue,
#                 booking_status
#             )
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """,
#             (
#                 hotel_id,
#                 customer_id,
#                 row["arrival_date"],
#                 row["total_nights"],
#                 int(float(row["total_guests"])),
#                 row["meal"],
#                 row["market_segment"],
#                 row["reserved_room_type"],
#                 row["adr"],
#                 row["estimated_revenue"],
#                 row["booking_status"]
#             )
#         )

# conn.commit()

# cur.close()
# conn.close()

# print("Data inserted successfully")


import csv
import psycopg

conn = psycopg.connect(
    host="localhost",
    port="5433",
    dbname="Hotels_db",
    user="pushpa",
    password="pushpa"
)

cur = conn.cursor()

batch_size = 5000
count = 0

with open("data/hotel_bookings_cleaned.csv", "r", encoding="utf-8") as file:

    reader = csv.DictReader(file)

    for row in reader:

        cur.execute(
            """
            INSERT INTO hotels (hotel)
            VALUES (%s)
            RETURNING hotel_id
            """,
            (row["hotel"],)
        )

        hotel_id = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO customers
            (country, customer_type, is_repeated_guest, guest_type)
            VALUES (%s, %s, %s, %s)
            RETURNING customer_id
            """,
            (
                row["country"],
                row["customer_type"],
                row["is_repeated_guest"],
                row["guest_type"]
            )
        )

        customer_id = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO bookings
            (
                hotel_id,
                customer_id,
                arrival_date,
                total_nights,
                total_guests,
                meal,
                market_segment,
                reserved_room_type,
                adr,
                estimated_revenue,
                booking_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                hotel_id,
                customer_id,
                row["arrival_date"],
                row["total_nights"],
                int(float(row["total_guests"])),
                row["meal"],
                row["market_segment"],
                row["reserved_room_type"],
                row["adr"],
                row["estimated_revenue"],
                row["booking_status"]
            )
        )

        count += 1

        if count % batch_size == 0:
            conn.commit()
            print(f"{count} rows inserted")

conn.commit()

cur.close()
conn.close()

print(f"All data inserted successfully: {count} rows")