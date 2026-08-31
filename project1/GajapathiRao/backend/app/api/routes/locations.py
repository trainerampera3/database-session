from fastapi import APIRouter

from app.db import create_connection

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("")
def get_locations():
    connection = create_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
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
                """
            )
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
            data = [dict(zip(columns, row)) for row in rows]
            return {"count": len(data), "data": data}
    finally:
        connection.close()
