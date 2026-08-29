CREATE VIEW vw_weather_hourly AS
SELECT
    l.city,
    l.state,
    l.country,
    l.latitude,
    l.longitude,
    w.observed_at,
    w.temperature,
    w.humidity,
    w.wind_speed
FROM weather_hourly w
JOIN location l
    ON w.location_id = l.location_id;