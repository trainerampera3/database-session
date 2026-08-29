import fastapi as fastapi
from app.database.connection import create_connection
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str

app = fastapi.FastAPI(
    title="Weather ETL API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        
        
from datetime import date


from datetime import date


@app.get("/weather/history")
def get_weather_history(
    start_date: date,
    end_date: date,
    location_id: int | None = None,
    limit: int = 100,
    offset: int = 0
):

    connection = create_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    l.location_id,
                    l.city,
                    l.state,
                    l.country,
                    wh.observed_at,
                    wh.temperature
                FROM weather_historical wh
                JOIN location l
                    ON wh.location_id = l.location_id
                WHERE wh.observed_at >= %s
                AND wh.observed_at < %s + INTERVAL '1 day'
                AND (%s IS NULL OR wh.location_id = %s)
                ORDER BY l.city, wh.observed_at
                LIMIT %s
                OFFSET %s;
            """, (
                start_date,
                end_date,
                location_id,
                location_id,
                limit,
                offset
            ))

            rows = cursor.fetchall()

            columns = [
                "location_id",
                "city",
                "state",
                "country",
                "observed_at",
                "temperature",
            ]

            data = [
                dict(zip(columns, row))
                for row in rows
            ]

            return {
                "count": len(data),
                "start_date": start_date,
                "end_date": end_date,
                "location_id": location_id,
                "limit": limit,
                "offset": offset,
                "data": data
            }

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

            data = [
                dict(zip(columns, row))
                for row in rows
            ]

            return {
                "count": len(data),
                "data": data
            }

    finally:
        connection.close()
        
@app.get("/etl/logs")
def get_etl_logs():

    connection = create_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    run_id,
                    pipeline_name,
                    started_at,
                    completed_at,
                    status,
                    records_processed,
                    error_message
                FROM etl_run_log
                ORDER BY started_at DESC;
            """)

            rows = cursor.fetchall()

            columns = [
                "run_id",
                "pipeline_name",
                "started_at",
                "completed_at",
                "status",
                "records_processed",
                "error_message",
            ]

            data = [
                dict(zip(columns, row))
                for row in rows
            ]

            return {
                "count": len(data),
                "data": data
            }

    finally:
        connection.close()
        
        
        
        
        


@app.post("/query")
def execute_query(request: QueryRequest):

    query = request.query.strip()

    if not query:
        raise fastapi.HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    # Only SELECT queries are allowed
    if not query.lower().startswith("select"):
        raise fastapi.HTTPException(
            status_code=400,
            detail="Only SELECT queries are allowed."
        )

    connection = create_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(query)

            rows = cursor.fetchall()

            columns = [
                description[0]
                for description in cursor.description
            ]

            data = [
                dict(zip(columns, row))
                for row in rows
            ]

            return {
                "count": len(data),
                "data": data
            }

    except Exception as error:

        raise fastapi.HTTPException(
            status_code=400,
            detail=str(error)
        )

    finally:

        connection.close()
        
@app.get("/news")
def get_weather_news(
    limit: int = 20,
    offset: int = 0
):

    connection = create_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    news_id,
                    title,
                    source,
                    published_at,
                    url,
                    category,
                    scraped_at
                FROM weather_news
                ORDER BY published_at DESC
                LIMIT %s
                OFFSET %s;
                """,
                (
                    limit,
                    offset
                )
            )

            rows = cursor.fetchall()

            columns = [
                "news_id",
                "title",
                "source",
                "published_at",
                "url",
                "category",
                "scraped_at",
            ]

            data = [
                dict(zip(columns, row))
                for row in rows
            ]

            return {
                "count": len(data),
                "limit": limit,
                "offset": offset,
                "data": data
            }

    finally:
        connection.close()