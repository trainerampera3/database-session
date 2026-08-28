import pandas as pd


def transform_hourly_data(data: dict) -> pd.DataFrame:
    hourly = data["hourly"]

    df = pd.DataFrame({
        "observed_at": hourly["time"],
        "temperature": hourly["temperature_2m"],
        "humidity": hourly["relative_humidity_2m"],
        "wind_speed": hourly["wind_speed_10m"],
    })

    df["observed_at"] = pd.to_datetime(df["observed_at"])

    return df

def transform_all_locations(results):

    all_data = []

    for result in results:

        location = result["location"]
        weather = result["weather"]

        hourly = weather["hourly"]

        df = pd.DataFrame({
            "observed_at": pd.to_datetime(hourly["time"]),
            "temperature": hourly["temperature_2m"],
            "humidity": hourly["relative_humidity_2m"],
            "wind_speed": hourly["wind_speed_10m"],
        })

        df["location_id"] = location["location_id"]

        all_data.append(df)

    return pd.concat(all_data, ignore_index=True)

if __name__ == "__main__":
    from extract import fetch_weather , fetch_weather_for_all_locations

    # latitude = 13.110721
    # longitude = 80.2459

    # data = fetch_weather(latitude, longitude)

    # df = transform_hourly_data(data)

    # print(df.head())
    # print("\nShape:", df.shape)
    # print("\nData types:")
    # print(df.dtypes)
    
    

    results = fetch_weather_for_all_locations()

    df = transform_all_locations(results)

    print(df.head())
    print("\nShape:", df.shape)
    print("\nRecords by location:")
    print(df.groupby("location_id").size())