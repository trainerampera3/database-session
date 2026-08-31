from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "used_cars_cleaned.csv"


def load_data():
    # Load the cleaned dataset
    return pd.read_csv(DATA_FILE)


def basic_statistics(df):
    # Display basic information about the dataset
    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("\nPrice statistics:")
    print(df["listed_price"].describe())


def category_analysis(df):
    # Check the main categorical columns
    print("\nTop brands:")
    print(df["oem"].value_counts().head(10))

    print("\nFuel types:")
    print(df["fuel"].value_counts())

    print("\nTransmission:")
    print(df["transmission"].value_counts())

    print("\nBody types:")
    print(df["body"].value_counts())

    print("\nTop cities:")
    print(df["city"].value_counts().head(10))


def plot_price_distribution(df):
    # Show how car prices are distributed
    fig, ax = plt.subplots()
    ax.hist(df["price_lakhs"], bins=30)
    ax.set_title("Used Car Price Distribution")
    ax.set_xlabel("Price (Lakhs)")
    ax.set_ylabel("Number of Cars")
    fig.tight_layout()
    return fig


def plot_price_by_model(df, top_n=10):
    # Compare average prices of models
    data = (
        df.groupby("model")["price_lakhs"]
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
        .sort_values()
    )

    fig, ax = plt.subplots()
    ax.barh(data.index, data.values)
    ax.set_title("Average Price by Model")
    ax.set_xlabel("Average Price (Lakhs)")
    ax.set_ylabel("Model")
    fig.tight_layout()
    return fig


def plot_price_vs_mileage(df):
    # Show the relationship between mileage and price
    fig, ax = plt.subplots()
    ax.scatter(
        df["km_thousands"],
        df["price_lakhs"],
        alpha=0.4
    )
    ax.set_title("Price vs Mileage")
    ax.set_xlabel("Mileage (Thousand KM)")
    ax.set_ylabel("Price (Lakhs)")
    fig.tight_layout()
    return fig


def plot_model_listings(df, top_n=10):
    # Show which models have the most listings
    data = (
        df["model"]
        .value_counts()
        .head(top_n)
        .sort_values()
    )

    fig, ax = plt.subplots()
    ax.barh(data.index, data.values)
    ax.set_title("Models by Number of Listings")
    ax.set_xlabel("Number of Listings")
    ax.set_ylabel("Model")
    fig.tight_layout()
    return fig


def plot_brand_listings(df, top_n=10):
    # Show which brands have the most inventory
    data = (
        df["oem"]
        .value_counts()
        .head(top_n)
        .sort_values()
    )

    fig, ax = plt.subplots()
    ax.barh(data.index, data.values)
    ax.set_title("Brands by Number of Listings")
    ax.set_xlabel("Number of Listings")
    ax.set_ylabel("Brand")
    fig.tight_layout()
    return fig


def plot_brand_price(df, top_n=10):
    # Compare average prices between major brands
    brands = (
        df["oem"]
        .value_counts()
        .head(top_n)
        .index
    )

    data = (
        df[df["oem"].isin(brands)]
        .groupby("oem")["price_lakhs"]
        .mean()
        .sort_values()
    )

    fig, ax = plt.subplots()
    ax.barh(data.index, data.values)
    ax.set_title("Average Price by Brand")
    ax.set_xlabel("Average Price (Lakhs)")
    ax.set_ylabel("Brand")
    fig.tight_layout()
    return fig


def plot_price_segments(df):
    # Show the number of cars in each price range
    order = [
        "budget",
        "mid_range",
        "premium",
        "luxury",
        "high_end"
    ]

    data = (
        df["price_segment"]
        .value_counts()
        .reindex(order, fill_value=0)
    )

    fig, ax = plt.subplots()
    ax.bar(data.index, data.values)
    ax.set_title("Listings by Price Segment")
    ax.set_xlabel("Price Segment")
    ax.set_ylabel("Number of Listings")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    return fig


def plot_city_listings(df, top_n=10):
    # Show the cities with the most listings
    data = (
        df["city"]
        .value_counts()
        .head(top_n)
        .sort_values()
    )

    fig, ax = plt.subplots()
    ax.barh(data.index, data.values)
    ax.set_title("Listings by City")
    ax.set_xlabel("Number of Listings")
    ax.set_ylabel("City")
    fig.tight_layout()
    return fig


def plot_city_price(df, top_n=10):
    # Compare average prices between major cities
    cities = (
        df["city"]
        .value_counts()
        .head(top_n)
        .index
    )

    data = (
        df[df["city"].isin(cities)]
        .groupby("city")["price_lakhs"]
        .mean()
        .sort_values()
    )

    fig, ax = plt.subplots()
    ax.barh(data.index, data.values)
    ax.set_title("Average Price by City")
    ax.set_xlabel("Average Price (Lakhs)")
    ax.set_ylabel("City")
    fig.tight_layout()
    return fig


def plot_fuel_distribution(df):
    # Show the distribution of fuel types
    data = df["fuel"].value_counts()

    fig, ax = plt.subplots()
    ax.bar(data.index, data.values)
    ax.set_title("Fuel Type Distribution")
    ax.set_xlabel("Fuel Type")
    ax.set_ylabel("Number of Listings")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    return fig


def plot_car_comparison(df, models):
    # Compare selected models using price, mileage and age
    data = (
        df[df["model"].isin(models)]
        .groupby("model")
        .agg(
            average_price=("price_lakhs", "mean"),
            average_mileage=("km_thousands", "mean"),
            average_age=("vehicle_age", "mean")
        )
    )

    fig, ax = plt.subplots()

    x = range(len(data))

    ax.bar(
        [i - 0.25 for i in x],
        data["average_price"],
        width=0.25,
        label="Price (Lakhs)"
    )

    ax.bar(
        x,
        data["average_mileage"],
        width=0.25,
        label="Mileage (000 KM)"
    )

    ax.bar(
        [i + 0.25 for i in x],
        data["average_age"],
        width=0.25,
        label="Age (Years)"
    )

    ax.set_xticks(list(x))
    ax.set_xticklabels(data.index)
    ax.set_title("Selected Car Comparison")
    ax.legend()

    fig.tight_layout()
    return fig


def main():
    df = load_data()
    print("Dataset shape:", df.shape)
    basic_statistics(df)
    category_analysis(df)


if __name__ == "__main__":
    main()