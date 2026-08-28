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