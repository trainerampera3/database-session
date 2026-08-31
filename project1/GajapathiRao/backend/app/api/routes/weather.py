from datetime import date

import fastapi
from fastapi import APIRouter

from app.db import create_connection

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/hourly")
def get_hourly_weather():
    connection = create_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
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
                """
            )
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
            return {"count": len(rows), "data": [dict(zip(columns, row)) for row in rows]}
    finally:
        connection.close()


@router.get("/current")
def get_current_weather():
    connection = create_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
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
                """
            )
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
            return [dict(zip(columns, row)) for row in rows]
    finally:
        connection.close()


@router.get("/history")
def get_weather_history(
    start_date: date,
    end_date: date,
    location_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
):
    connection = create_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
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
                  AND (%s::INTEGER IS NULL OR wh.location_id = %s)
                ORDER BY l.city, wh.observed_at
                LIMIT %s
                OFFSET %s;
                """,
                (start_date, end_date, location_id, location_id, limit, offset),
            )
            rows = cursor.fetchall()
            columns = [
                "location_id",
                "city",
                "state",
                "country",
                "observed_at",
                "temperature",
            ]
            data = [dict(zip(columns, row)) for row in rows]
            return {
                "count": len(data),
                "start_date": start_date,
                "end_date": end_date,
                "location_id": location_id,
                "limit": limit,
                "offset": offset,
                "data": data,
            }
    finally:
        connection.close()
