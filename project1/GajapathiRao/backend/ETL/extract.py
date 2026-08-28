import requests


BASE_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_weather(latitude: float, longitude: float) -> dict:

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "past_days": 10,
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

from app.database.connection import create_connection


def get_locations():

    connection = create_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    location_id,
                    city,
                    state,
                    country,
                    latitude,
                    longitude,
                    timezone
                FROM location
                ORDER BY location_id;
            """)

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

            return [
                dict(zip(columns, row))
                for row in rows
            ]

    finally:
        connection.close()

def fetch_weather_for_all_locations():

    locations = get_locations()

    results = []

    for location in locations:

        print(f"Fetching weather for {location['city']}...")

        data = fetch_weather(
            location["latitude"],
            location["longitude"]
        )

        results.append({
            "location": location,
            "weather": data
        })

    return results


if __name__ == "__main__":

    latitude = 13.0827
    longitude = 80.2707

    # data = fetch_weather(latitude, longitude)

    # print("Latitude:", data["latitude"])
    # print("Longitude:", data["longitude"])
    # print("Timezone:", data["timezone"])

    # print("\nCurrent Weather:")
    # print(data["current"])

    # print("\nHourly data:")
    # print("Number of hourly records:", len(data["hourly"]["time"]))
    
    
    # locations = get_locations()

    # for location in locations:
    #     print(
    #         location["city"],
    #         location["latitude"],
    #         location["longitude"]
    #     )
    
    results = fetch_weather_for_all_locations()

    print(f"\nLocations processed: {len(results)}")

    for result in results:
        print(
            result["location"]["city"],
            "→",
            len(result["weather"]["hourly"]["time"]),
            "hourly records"
        )