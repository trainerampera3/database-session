from app.database.connection import create_connection


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
        

if __name__ == "__main__":

    from extract import fetch_weather_for_all_locations
    from transform import transform_all_locations

    # Extract weather for all locations
    results = fetch_weather_for_all_locations()

    # Transform all locations
    df = transform_all_locations(results)

    # Load hourly data
    load_hourly_data(df)

    # Load current weather for every location
    for result in results:

        location_id = result["location"]["location_id"]
        data = result["weather"]

        load_current_data(data, location_id)

    print("ETL pipeline completed successfully.")