CREATE TABLE location (
    location_id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    country VARCHAR(100) NOT NULL,
    latitude NUMERIC(9,6) NOT NULL,
    longitude NUMERIC(9,6) NOT NULL,
    timezone VARCHAR(100),
    elevation NUMERIC(8,2),

    CONSTRAINT unique_location
        UNIQUE (city, country)
);

CREATE TABLE weather_current (
    weather_id BIGSERIAL PRIMARY KEY,
    location_id INT NOT NULL,
    observed_at TIMESTAMP NOT NULL,
    temperature NUMERIC(5,2),
    wind_speed NUMERIC(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (location_id)
        REFERENCES location(location_id)
);



CREATE TABLE weather_hourly (
    weather_hourly_id BIGSERIAL PRIMARY KEY,
    location_id INT NOT NULL,
    observed_at TIMESTAMP NOT NULL,
    temperature NUMERIC(5,2),
    humidity NUMERIC(5,2),
    wind_speed NUMERIC(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (location_id)
        REFERENCES location(location_id),

    UNIQUE (location_id, observed_at)
);

CREATE TABLE weather_historical (
    historical_id BIGSERIAL PRIMARY KEY,
    location_id INT NOT NULL,
    observed_at TIMESTAMP NOT NULL,
    temperature NUMERIC(5,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_weather_historical_location
        FOREIGN KEY (location_id)
        REFERENCES location(location_id),

    CONSTRAINT uq_weather_historical_location_time
        UNIQUE (location_id, observed_at)
);