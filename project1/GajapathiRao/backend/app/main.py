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
                    city,
                    state,
                    country,
                    observed_at,
                    temperature,
                    humidity,
                    wind_speed
                FROM vw_weather_hourly
                ORDER BY observed_at;
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
        

@app.get("/weather/current")
def get_current_weather():

    connection = create_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    city,
                    state,
                    country,
                    observed_at,
                    temperature,
                    humidity,
                    wind_speed
                FROM vw_weather_hourly
                ORDER BY observed_at DESC
                LIMIT 1;
            """)

            row = cursor.fetchone()

            if row is None:
                return {"message": "No weather data available"}

            columns = [
                "city",
                "state",
                "country",
                "observed_at",
                "temperature",
                "humidity",
                "wind_speed",
            ]

            return dict(zip(columns, row))

    finally:
        connection.close()
