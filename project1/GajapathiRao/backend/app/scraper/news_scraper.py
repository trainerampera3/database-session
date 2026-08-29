import logging
from datetime import datetime, timezone
from urllib.parse import urlparse

import feedparser


NEWS_FEED_URL = (
    "https://indianexpress.com/section/weather/feed/"
)

DEFAULT_LIMIT = 20


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------

def is_valid_url(url):
    """Check whether a URL is valid."""

    if not url:
        return False

    parsed = urlparse(url)

    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def parse_published_date(entry):
    """Convert RSS published date into ISO format."""

    if not hasattr(entry, "published_parsed"):
        return None

    if not entry.published_parsed:
        return None

    try:
        published_at = datetime(
            *entry.published_parsed[:6],
            tzinfo=timezone.utc,
        )

        return published_at.isoformat()

    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------
# Scraper
# ---------------------------------------------------------

def scrape_weather_news(limit=DEFAULT_LIMIT):

    logger.info("Starting weather news scraping")

    feed = feedparser.parse(NEWS_FEED_URL)

    # Check feed status
    if getattr(feed, "bozo", False):

        logger.warning(
            "RSS feed returned a parsing warning: %s",
            getattr(feed, "bozo_exception", "Unknown error"),
        )

    entries = getattr(feed, "entries", [])

    if not entries:

        logger.warning("No articles found in RSS feed")

        return []

    news = []
    seen_urls = set()

    for entry in entries:

        title = entry.get("title", "").strip()

        url = entry.get("link", "").strip()

        published_at = parse_published_date(entry)

        # ---------------------------------------------
        # Validate title
        # ---------------------------------------------

        if not title:

            logger.warning(
                "Skipping article because title is missing"
            )

            continue

        # ---------------------------------------------
        # Validate URL
        # ---------------------------------------------

        if not is_valid_url(url):

            logger.warning(
                "Skipping article with invalid URL: %s",
                url,
            )

            continue

        # ---------------------------------------------
        # Duplicate check
        # ---------------------------------------------

        if url in seen_urls:

            logger.info(
                "Skipping duplicate article: %s",
                title,
            )

            continue

        seen_urls.add(url)

        # ---------------------------------------------
        # Create clean record
        # ---------------------------------------------

        news_item = {
            "title": title,
            "source": "Indian Express",
            "published_at": published_at,
            "url": url,
            "category": "Weather",
        }

        news.append(news_item)

        # ---------------------------------------------
        # Limit
        # ---------------------------------------------

        if len(news) >= limit:
            break

    logger.info(
        "Scraping completed successfully: %d articles",
        len(news),
    )

    return news


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    print()
    print("=" * 80)
    print("WEATHER NEWS SCRAPER")
    print("=" * 80)
    print()

    articles = scrape_weather_news(limit=10)

    print(f"Articles found: {len(articles)}")
    print()

    for index, article in enumerate(
        articles,
        start=1,
    ):

        print("-" * 80)

        print(f"Article       : {index}")
        print(f"Title         : {article['title']}")
        print(f"Source        : {article['source']}")
        print(f"Published At  : {article['published_at']}")
        print(f"Category      : {article['category']}")
        print(f"URL           : {article['url']}")

    print()
    print("=" * 80)
    print("SCRAPING FINISHED")
    print("=" * 80)