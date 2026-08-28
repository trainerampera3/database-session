import requests


BASE_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_weather(latitude: float, longitude: float) -> dict:

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "timezone": "auto",
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


if __name__ == "__main__":

    latitude = 13.0827
    longitude = 80.2707

    data = fetch_weather(latitude, longitude)

    print("Latitude:", data["latitude"])
    print("Longitude:", data["longitude"])
    print("Timezone:", data["timezone"])

    print("\nCurrent Weather:")
    print(data["current"])

    print("\nHourly data:")
    print("Number of hourly records:", len(data["hourly"]["time"]))