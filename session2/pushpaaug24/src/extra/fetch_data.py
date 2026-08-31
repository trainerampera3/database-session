import psycopg

conn= psycopg.connect(
           host="localhost",
          port="5433",
          dbname="services",
        user="pushpa", 
        password="pushpa")


cur = conn.cursor()
cur.execute("SELECT * FROM hotels")

rows = cur.fetchall()

for row in rows:
    print(row)

cur.close()
conn.close()


# def fetch_hotels():
#     conn = get_connection()
#     cur = conn.cursor()

#     cur.execute("""
#         SELECT *
#         FROM hotels
#     """)

#     rows = cur.fetchall()

#     cur.close()
#     conn.close()

#     return rows