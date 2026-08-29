from extract import (
    fetch_historical_weather,
    get_locations,
)

from transform import transform_historical_data
from load import load_historical_data


if __name__ == "__main__":

    locations = get_locations()

    for location in locations:

        print(
            f"Fetching historical data for "
            f"{location['city']}..."
        )

        data = fetch_historical_weather(
            location["latitude"],
            location["longitude"],
            "2025-01-01",
            "2025-01-07"
        )

        df = transform_historical_data(
            data,
            location["location_id"]
        )

        load_historical_data(df)

    print("Historical ETL completed successfully.")