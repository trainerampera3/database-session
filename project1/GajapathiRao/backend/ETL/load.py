from app.database.connection import create_connection
from datetime import datetime


def load_hourly_data(df):
    connection = create_connection()

    if connection is None:
        return

    try:
        with connection.cursor() as cursor:

            for row in df.itertuples(index=False):

                cursor.execute(
                    """
                    INSERT INTO weather_hourly
                    (
                        location_id,
                        observed_at,
                        temperature,
                        humidity,
                        wind_speed
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (location_id, observed_at)
                    DO UPDATE SET
                        temperature = EXCLUDED.temperature,
                        humidity = EXCLUDED.humidity,
                        wind_speed = EXCLUDED.wind_speed;
                    """,
                    (
                        row.location_id,
                        row.observed_at,
                        row.temperature,
                        row.humidity,
                        row.wind_speed,
                    ),
                )

        connection.commit()

        print(f"{len(df)} hourly records loaded successfully.")

    except Exception as e:
        connection.rollback()
        print(f"Load error: {e}")

    finally:
        connection.close()
        
        
def load_current_data(data: dict, location_id: int):

    connection = create_connection()

    if connection is None:
        return

    try:
        current = data["current"]

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO weather_current
                (
                    location_id,
                    observed_at,
                    temperature,
                    humidity,
                    wind_speed
                )
                VALUES (%s, %s, %s, %s , %s)
                ON CONFLICT (location_id, observed_at)
                DO UPDATE SET
                temperature = EXCLUDED.temperature,
                humidity = EXCLUDED.humidity,
                wind_speed = EXCLUDED.wind_speed;
                """,
                (
                    location_id,
                    current["time"],
                    current["temperature_2m"],
                    current["relative_humidity_2m"],
                    current["wind_speed_10m"],
                ),
            )

        connection.commit()

        print("Current weather loaded successfully.")

    except Exception as e:
        connection.rollback()
        print(f"Current weather load error: {e}")

    finally:
        connection.close()
     
   

def load_historical_data(df):

    connection = create_connection()

    if connection is None:
        return

    try:
        with connection.cursor() as cursor:

            for row in df.itertuples(index=False):

                cursor.execute(
                    """
                    INSERT INTO weather_historical
                    (
                        location_id,
                        observed_at,
                        temperature
                    )
                    VALUES (%s, %s, %s)
                    ON CONFLICT (location_id, observed_at)
                    DO UPDATE SET
                        temperature = EXCLUDED.temperature;
                    """,
                    (
                        row.location_id,
                        row.observed_at,
                        row.temperature,
                    ),
                )

        connection.commit()

        print(
            f"{len(df)} historical records loaded successfully."
        )

    except Exception as e:
        connection.rollback()
        print(f"Historical load error: {e}")

    finally:
        connection.close()
        


def start_etl_log():

    connection = create_connection()

    if connection is None:
        return None

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO etl_run_log
                (
                    pipeline_name,
                    started_at,
                    status
                )
                VALUES (%s, %s, %s)
                RETURNING run_id;
                """,
                (
                    "weather_etl",
                    datetime.now(),
                    "RUNNING",
                ),
            )

            run_id = cursor.fetchone()[0]

        connection.commit()

        return run_id

    finally:
        connection.close()
        

def complete_etl_log(run_id, records_processed):

    connection = create_connection()

    if connection is None:
        return

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE etl_run_log
                SET
                    completed_at = %s,
                    status = 'SUCCESS',
                    records_processed = %s
                WHERE run_id = %s;
                """,
                (
                    datetime.now(),
                    records_processed,
                    run_id,
                ),
            )

        connection.commit()

    finally:
        connection.close()
        

def fail_etl_log(run_id, error_message):

    connection = create_connection()

    if connection is None:
        return

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE etl_run_log
                SET
                    completed_at = %s,
                    status = 'FAILED',
                    error_message = %s
                WHERE run_id = %s;
                """,
                (
                    datetime.now(),
                    str(error_message),
                    run_id,
                ),
            )

        connection.commit()

    finally:
        connection.close()
        
        
if __name__ == "__main__":

    from extract import fetch_weather_for_all_locations
    from transform import transform_all_locations

    run_id = start_etl_log()

    try:

        results = fetch_weather_for_all_locations()

        df = transform_all_locations(results)

        load_hourly_data(df)

        for result in results:

            location_id = result["location"]["location_id"]
            data = result["weather"]

            load_current_data(
                data,
                location_id
            )

        complete_etl_log(
            run_id,
            len(df)
        )

        print("ETL pipeline completed successfully.")

    except Exception as e:

        fail_etl_log(
            run_id,
            e
        )

        print(
            f"ETL pipeline failed: {e}"
        )

        raise