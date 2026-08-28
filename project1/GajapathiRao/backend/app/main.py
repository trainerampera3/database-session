import fastapi as fastapi
from app.database.connection import create_connection

app = fastapi.FastAPI(
    title="Weather ETL API",
    version="1.0.0"
)

# app.include_router(weather_router)

@app.get("/")
def read_root():
     return {
        "message": "Weather ETL API is running"
    }
     
     
@app.get("/weather/hourly")
def get_hourly_weather():

    connection = create_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    l.city,
                    l.state,
                    l.country,
                    wh.observed_at,
                    wh.temperature,
                    wh.humidity,
                    wh.wind_speed
                FROM weather_hourly wh
                JOIN location l
                    ON wh.location_id = l.location_id
                ORDER BY l.city, wh.observed_at;
            """)

            rows = cursor.fetchall()

            columns = [
                "city",
                "state",
                "country",
                "observed_at",
                "temperature",
                "humidity",
                "wind_speed",
            ]

            return {
                "count": len(rows),
                "data": [
                    dict(zip(columns, row))
                    for row in rows
                ]
            }

    finally:
        connection.close()
        



@app.get("/weather/current")
def get_current_weather():

    connection = create_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    l.city,
                    l.state,
                    l.country,
                    wc.observed_at,
                    wc.temperature,
                    wc.humidity,
                    wc.wind_speed
                FROM weather_current wc
                JOIN location l
                    ON wc.location_id = l.location_id
                ORDER BY l.city;
            """)

            rows = cursor.fetchall()

            columns = [
                "city",
                "state",
                "country",
                "observed_at",
                "temperature",
                "humidity",
                "wind_speed",
            ]

            return [
                dict(zip(columns, row))
                for row in rows
            ]

    finally:
        connection.close()
@app.get("/locations")
def get_locations():

    connection = create_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    location_id,
                    city,
                    state,
                    country,
                    latitude,
                    longitude,
                    timezone
                FROM location
                ORDER BY city;
            """)

            rows = cursor.fetchall()

            columns = [
                "location_id",
                "city",
                "state",
                "country",
                "latitude",
                "longitude",
                "timezone",
            ]

            return [
                dict(zip(columns, row))
                for row in rows
            ]

    finally:
        connection.close()