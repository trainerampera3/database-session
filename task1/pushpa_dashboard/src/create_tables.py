from db import get_connection


conn = get_connection()

with conn.cursor() as cur:

    cur.execute("""
        DROP TABLE IF EXISTS train_schedule;
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS train_info (
            train_no INTEGER PRIMARY KEY,
            train_name TEXT,
            source_station_name TEXT,
            destination_station_name TEXT,
            days TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE train_schedule (
            sn INTEGER NOT NULL,
            train_no INTEGER NOT NULL,
            station_code TEXT,
            class_1a INTEGER,
            class_2a INTEGER,
            class_3a INTEGER,
            class_sl INTEGER,
            station_name TEXT,
            route_number INTEGER,
            arrival_time TIME,
            departure_time TIME,
            distance DOUBLE PRECISION,

            PRIMARY KEY (train_no, sn),

            FOREIGN KEY (train_no)
                REFERENCES train_info(train_no)
        );
    """)

conn.commit()
conn.close()

print("PostgreSQL tables created successfully.")