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
                    DO NOTHING;
                    """,
                    (
                        1,
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
        
if __name__ == "__main__":
    from extract import fetch_weather
    from transform import transform_hourly_data

    latitude = 13.110721
    longitude = 80.2459

    data = fetch_weather(latitude, longitude)

    df = transform_hourly_data(data)

    # load_hourly_data(df)
    load_current_data(data, 1)