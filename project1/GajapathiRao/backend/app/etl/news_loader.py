import logging

from app.database.connection import create_connection
from app.scraper.news_scraper import scrape_weather_news


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def load_weather_news():

    logger.info("Starting weather news ETL")

    articles = scrape_weather_news(limit=20)

    if not articles:
        logger.warning("No articles available to load")
        return 0

    connection = create_connection()

    inserted_count = 0

    try:

        with connection.cursor() as cursor:

            for article in articles:

                cursor.execute(
                    """
                    INSERT INTO weather_news (
                        title,
                        source,
                        published_at,
                        url,
                        category
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    ON CONFLICT (url)
    DO NOTHING;
                    """,
                    (
                        article["title"],
                        article["source"],
                        article["published_at"],
                        article["url"],
                        article["category"],
                    ),
                )

                if cursor.rowcount == 1:
                    inserted_count += 1

        connection.commit()

        logger.info(
            "News ETL completed. Inserted: %d",
            inserted_count,
        )

        return inserted_count

    except Exception:

        connection.rollback()

        logger.exception(
            "News ETL failed"
        )

        raise

    finally:

        connection.close()


if __name__ == "__main__":

    print()
    print("=" * 70)
    print("WEATHER NEWS ETL")
    print("=" * 70)

    count = load_weather_news()

    print()
    print(f"New articles inserted: {count}")
    print()