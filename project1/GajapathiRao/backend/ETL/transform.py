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

if __name__ == "__main__":
    from extract import fetch_weather

    latitude = 13.110721
    longitude = 80.2459

    data = fetch_weather(latitude, longitude)

    df = transform_hourly_data(data)

    print(df.head())
    print("\nShape:", df.shape)
    print("\nData types:")
    print(df.dtypes)