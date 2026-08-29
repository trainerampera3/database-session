CREATE TABLE weather_news (
    news_id BIGSERIAL PRIMARY KEY,

    title TEXT NOT NULL,

    source VARCHAR(100) NOT NULL,

    published_at TIMESTAMPTZ,

    url TEXT NOT NULL UNIQUE,

    category VARCHAR(50) NOT NULL DEFAULT 'Weather',

    scraped_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);