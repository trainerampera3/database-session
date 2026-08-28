CREATE INDEX idx_weather_hourly_location_time
ON weather_hourly (location_id, observed_at);

CREATE INDEX idx_weather_historical_location_time
ON weather_historical (location_id, observed_at);

CREATE INDEX idx_weather_historical_observed_at
ON weather_historical (observed_at);