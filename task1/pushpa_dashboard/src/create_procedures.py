from db import get_connection


conn = get_connection()

with conn.cursor() as cur:

    cur.execute("""
        CREATE OR REPLACE FUNCTION insert_train_info(
            p_train_no INTEGER,
            p_train_name TEXT,
            p_source TEXT,
            p_destination TEXT,
            p_days TEXT
        )
        RETURNS VOID
        AS $$
        BEGIN

            INSERT INTO train_info (
                train_no,
                train_name,
                source_station_name,
                destination_station_name,
                days
            )
            VALUES (
                p_train_no,
                p_train_name,
                p_source,
                p_destination,
                p_days
            )

            ON CONFLICT (train_no)
            DO UPDATE SET
                train_name = EXCLUDED.train_name,
                source_station_name = EXCLUDED.source_station_name,
                destination_station_name = EXCLUDED.destination_station_name,
                days = EXCLUDED.days;

        END;
        $$
        LANGUAGE plpgsql;
    """)


    cur.execute("""
        CREATE OR REPLACE FUNCTION insert_train_schedule(
            p_sn INTEGER,
            p_train_no INTEGER,
            p_station_code TEXT,
            p_class_1a INTEGER,
            p_class_2a INTEGER,
            p_class_3a INTEGER,
            p_class_sl INTEGER,
            p_station_name TEXT,
            p_route_number INTEGER,
            p_arrival_time TIME,
            p_departure_time TIME,
            p_distance DOUBLE PRECISION
        )
        RETURNS VOID
        AS $$
        BEGIN

            INSERT INTO train_schedule (
                sn,
                train_no,
                station_code,
                class_1a,
                class_2a,
                class_3a,
                class_sl,
                station_name,
                route_number,
                arrival_time,
                departure_time,
                distance
            )
            VALUES (
                p_sn,
                p_train_no,
                p_station_code,
                p_class_1a,
                p_class_2a,
                p_class_3a,
                p_class_sl,
                p_station_name,
                p_route_number,
                p_arrival_time,
                p_departure_time,
                p_distance
            )

            ON CONFLICT (train_no, sn)
            DO UPDATE SET
                station_code = EXCLUDED.station_code,
                class_1a = EXCLUDED.class_1a,
                class_2a = EXCLUDED.class_2a,
                class_3a = EXCLUDED.class_3a,
                class_sl = EXCLUDED.class_sl,
                station_name = EXCLUDED.station_name,
                route_number = EXCLUDED.route_number,
                arrival_time = EXCLUDED.arrival_time,
                departure_time = EXCLUDED.departure_time,
                distance = EXCLUDED.distance;

        END;
        $$
        LANGUAGE plpgsql;
    """)


conn.commit()
conn.close()

print("PostgreSQL functions created successfully.")