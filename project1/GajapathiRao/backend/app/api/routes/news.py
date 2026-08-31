from fastapi import APIRouter

from app.db import create_connection

router = APIRouter(prefix="/news", tags=["news"])


@router.get("")
def get_weather_news(limit: int = 20, offset: int = 0):
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
                (limit, offset),
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
            data = [dict(zip(columns, row)) for row in rows]
            return {"count": len(data), "limit": limit, "offset": offset, "data": data}
    finally:
        connection.close()
