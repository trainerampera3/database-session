import sys
from pathlib import Path
import streamlit as st
import matplotlib.pyplot as plt

# Add the src directory so the dashboard can import the database functions
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
sys.path.append(str(SRC_DIR))

# Import the functions used to retrieve and analyse database data
from data_retrieval import (
    basic_statistics,
    get_filter_options,
    get_filtered_cars,
    get_vehicle_specs,
    get_customer_comparison,
    plot_price_distribution,
    plot_price_vs_mileage,
    plot_brand_listings,
    plot_model_listings,
    plot_model_price,
    plot_price_segments,
    plot_city_listings,
    plot_city_price,
    plot_fuel_distribution
)

# Configure the Streamlit page
st.set_page_config(
    page_title="Used Car Market Analytics",
    page_icon="",
    layout="wide"
)

# Display the dashboard title
st.title("Used Car Market Analytics")
st.caption("Used car analysis dashboard powered by PostgreSQL")

# Let the user select the problem they want to analyse
perspective = st.sidebar.selectbox(
    "Select Perspective",
    [
        "Customer",
        "Seller / Dealer",
        "Market Analyst"
    ]
)

st.sidebar.header("Filters")

if perspective == "Customer":
    # Customer filters focus on finding a suitable car
    filters = {
        "brand": "All",
        "model": "All",
        "price_segment": "All",
        "fuel": "All",
        "transmission": "All",
        "body": "All",
        "city": "All"
    }

    # Get the available filter values from PostgreSQL
    options = get_filter_options(
        filters,
        perspective
    )

    filters["brand"] = st.sidebar.selectbox(
        "Brand",
        ["All"] + options["brand"]
    )

    # Refresh the available models after the brand selection
    options = get_filter_options(
        filters,
        perspective
    )

    filters["model"] = st.sidebar.selectbox(
        "Model",
        ["All"] + options["model"]
    )

    # Refresh the price segments based on the current selections
    options = get_filter_options(
        filters,
        perspective
    )

    filters["price_segment"] = st.sidebar.selectbox(
        "Price Segment",
        ["All"] + options["price_segment"]
    )

    # Refresh the fuel options based on the current selections
    options = get_filter_options(
        filters,
        perspective
    )

    filters["fuel"] = st.sidebar.selectbox(
        "Fuel",
        ["All"] + options["fuel"]
    )

    # Refresh the transmission options based on the current selections
    options = get_filter_options(
        filters,
        perspective
    )

    filters["transmission"] = st.sidebar.selectbox(
        "Transmission",
        ["All"] + options["transmission"]
    )

    # Refresh the body type options based on the current selections
    options = get_filter_options(
        filters,
        perspective
    )

    filters["body"] = st.sidebar.selectbox(
        "Body Type",
        ["All"] + options["body"]
    )

    # Refresh the city options based on the current selections
    options = get_filter_options(
        filters,
        perspective
    )

    filters["city"] = st.sidebar.selectbox(
        "City",
        ["All"] + options["city"]
    )

    # Calculate customer statistics using SQL aggregation
    stats_df = basic_statistics(filters)

    if stats_df.empty:
        st.warning("No cars match the selected filters.")
        st.stop()

    stats = stats_df.iloc[0]

    if int(stats["total_listings"]) == 0:
        st.warning("No cars match the selected filters.")
        st.stop()

    st.header("Customer Dashboard")
    st.write(
        "Find a suitable used car based on your preferences "
        "and compare available models."
    )

    # Show the main numbers for the selected customer requirements
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Cars Found",
        f"{int(stats['total_listings']):,}"
    )

    col2.metric(
        "Average Price",
        f"₹{stats['average_price']:.2f} L"
    )

    col3.metric(
        "Lowest Price",
        f"₹{stats['lowest_price']:.2f} L"
    )

    col4.metric(
        "Average Mileage",
        f"{stats['average_mileage']:.1f}k km"
    )

    # Show how the prices of matching cars are distributed
    st.subheader("Price Distribution")

    price_data = plot_price_distribution(filters)

    fig, ax = plt.subplots()

    ax.hist(
        price_data["price_lakhs"],
        bins=30
    )

    ax.set_xlabel("Price (Lakhs)")
    ax.set_ylabel("Number of Cars")
    ax.set_title("Used Car Price Distribution")

    fig.tight_layout()
    st.pyplot(fig)

    # Let the customer compare multiple models
    st.subheader("Model Comparison")

    compare_models = st.multiselect(
        "Select models to compare",
        options["model"],
        max_selections=4
    )

    if len(compare_models) >= 2:
        comparison = get_customer_comparison(
            filters,
            compare_models
        )

        st.dataframe(
            comparison,
            width="stretch",
            hide_index=True
        )

        # Compare average mileage and average price for the selected models
        fig, ax = plt.subplots()

        ax.scatter(
            comparison["average_mileage"],
            comparison["average_price"]
        )

        for _, row in comparison.iterrows():
            ax.annotate(
                row["model"],
                (
                    row["average_mileage"],
                    row["average_price"]
                )
            )

        ax.set_xlabel("Average Mileage (000 KM)")
        ax.set_ylabel("Average Price (Lakhs)")
        ax.set_title("Model Price vs Mileage")

        fig.tight_layout()
        st.pyplot(fig)

    else:
        st.info("Select at least two models to compare.")

    # Show technical specifications when a specific model is selected
    if filters["model"] != "All":
        st.subheader("Vehicle Specifications")

        specs = get_vehicle_specs(
            filters,
            20
        )

        if specs.empty:
            st.info("No vehicle specifications found.")
        else:
            st.dataframe(
                specs,
                width="stretch",
                hide_index=True
            )

    # Show the actual cars that match the customer's requirements
    st.subheader("Available Cars")

    cars = get_filtered_cars(
        filters,
        500
    )

    if cars.empty:
        st.info("No cars match the selected filters.")
    else:
        st.dataframe(
            cars,
            width="stretch",
            hide_index=True
        )

elif perspective == "Seller / Dealer":
    # Seller filters focus on inventory and pricing decisions
    filters = {
        "city": "All",
        "brand": "All",
        "model": "All",
        "price_segment": "All",
        "fuel": "All",
        "body": "All"
    }

    # Get the available city options from PostgreSQL
    options = get_filter_options(
        filters,
        perspective
    )

    filters["city"] = st.sidebar.selectbox(
        "City",
        ["All"] + options["city"]
    )

    # Refresh the brand options after selecting a city
    options = get_filter_options(
        filters,
        perspective
    )

    filters["brand"] = st.sidebar.selectbox(
        "Brand",
        ["All"] + options["brand"]
    )

    # Refresh the model options after selecting a brand
    options = get_filter_options(
        filters,
        perspective
    )

    filters["model"] = st.sidebar.selectbox(
        "Model",
        ["All"] + options["model"]
    )

    # Refresh the price segments using the selected filters
    options = get_filter_options(
        filters,
        perspective
    )

    filters["price_segment"] = st.sidebar.selectbox(
        "Price Segment",
        ["All"] + options["price_segment"]
    )

    # Refresh the fuel options using the selected filters
    options = get_filter_options(
        filters,
        perspective
    )

    filters["fuel"] = st.sidebar.selectbox(
        "Fuel",
        ["All"] + options["fuel"]
    )

    # Refresh the body type options using the selected filters
    options = get_filter_options(
        filters,
        perspective
    )

    filters["body"] = st.sidebar.selectbox(
        "Body Type",
        ["All"] + options["body"]
    )

    # Calculate inventory and pricing statistics
    stats_df = basic_statistics(filters)

    if stats_df.empty:
        st.warning("No listings match the selected filters.")
        st.stop()

    stats = stats_df.iloc[0]

    if int(stats["total_listings"]) == 0:
        st.warning("No listings match the selected filters.")
        st.stop()

    st.header("Seller / Dealer Dashboard")
    st.write(
        "Understand inventory concentration and pricing "
        "in the selected market."
    )

    # Show the main inventory and pricing indicators
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Listings",
        f"{int(stats['total_listings']):,}"
    )

    col2.metric(
        "Average Price",
        f"₹{stats['average_price']:.2f} L"
    )

    col3.metric(
        "Average Mileage",
        f"{stats['average_mileage']:.1f}k km"
    )

    top_model = plot_model_listings(
        filters,
        1
    )

    if top_model.empty:
        top_model_name = "N/A"
    else:
        top_model_name = top_model.iloc[0]["model"]

    col4.metric(
        "Top Model",
        str(top_model_name).title()
    )

    # Show which brands have the most inventory
    st.subheader("Inventory by Brand")

    brand_data = plot_brand_listings(
        filters
    )

    brand_data = brand_data.sort_values(
        "listings"
    )

    fig, ax = plt.subplots()

    ax.barh(
        brand_data["oem"],
        brand_data["listings"]
    )

    ax.set_xlabel("Number of Listings")
    ax.set_ylabel("Brand")
    ax.set_title("Brand Inventory")

    fig.tight_layout()
    st.pyplot(fig)

    # Show which models have the most inventory
    st.subheader("Inventory by Model")

    model_data = plot_model_listings(
        filters
    )

    model_data = model_data.sort_values(
        "listings"
    )

    fig, ax = plt.subplots()

    ax.barh(
        model_data["model"],
        model_data["listings"]
    )

    ax.set_xlabel("Number of Listings")
    ax.set_ylabel("Model")
    ax.set_title("Model Inventory")

    fig.tight_layout()
    st.pyplot(fig)

    # Compare the average prices of the major models
    st.subheader("Average Price by Model")

    model_price = plot_model_price(
        filters
    )

    model_price = model_price.sort_values(
        "average_price"
    )

    fig, ax = plt.subplots()

    ax.barh(
        model_price["model"],
        model_price["average_price"]
    )

    ax.set_xlabel("Average Price (Lakhs)")
    ax.set_ylabel("Model")
    ax.set_title("Average Model Price")

    fig.tight_layout()
    st.pyplot(fig)

    # Show which price segments contain the most inventory
    st.subheader("Price Segment")

    segment_data = plot_price_segments(
        filters
    )

    fig, ax = plt.subplots()

    ax.bar(
        segment_data["price_segment"],
        segment_data["listings"]
    )

    ax.set_xlabel("Price Segment")
    ax.set_ylabel("Listings")
    ax.set_title("Inventory by Price Segment")

    fig.tight_layout()
    st.pyplot(fig)

    # Show the detailed inventory matching the dealer filters
    st.subheader("Filtered Inventory")

    cars = get_filtered_cars(
        filters,
        500
    )

    if cars.empty:
        st.info("No listings match the selected filters.")
    else:
        st.dataframe(
            cars,
            width="stretch",
            hide_index=True
        )

else:
    # Analyst filters focus on geography and overall market patterns
    filters = {
        "state": "All",
        "city": "All",
        "brand": "All",
        "fuel": "All",
        "transmission": "All",
        "body": "All",
        "price_segment": "All"
    }

    # Get the available state options from PostgreSQL
    options = get_filter_options(
        filters,
        perspective
    )

    filters["state"] = st.sidebar.selectbox(
        "State",
        ["All"] + options["state"]
    )

    # Refresh city options after selecting a state
    options = get_filter_options(
        filters,
        perspective
    )

    filters["city"] = st.sidebar.selectbox(
        "City",
        ["All"] + options["city"]
    )

    # Refresh brand options after applying geography filters
    options = get_filter_options(
        filters,
        perspective
    )

    filters["brand"] = st.sidebar.selectbox(
        "Brand",
        ["All"] + options["brand"]
    )

    # Refresh fuel options using the current filters
    options = get_filter_options(
        filters,
        perspective
    )

    filters["fuel"] = st.sidebar.selectbox(
        "Fuel",
        ["All"] + options["fuel"]
    )

    # Refresh transmission options using the current filters
    options = get_filter_options(
        filters,
        perspective
    )

    filters["transmission"] = st.sidebar.selectbox(
        "Transmission",
        ["All"] + options["transmission"]
    )

    # Refresh body type options using the current filters
    options = get_filter_options(
        filters,
        perspective
    )

    filters["body"] = st.sidebar.selectbox(
        "Body Type",
        ["All"] + options["body"]
    )

    # Refresh price segment options using the current filters
    options = get_filter_options(
        filters,
        perspective
    )

    filters["price_segment"] = st.sidebar.selectbox(
        "Price Segment",
        ["All"] + options["price_segment"]
    )

    # Calculate the market statistics for the selected filters
    stats_df = basic_statistics(filters)

    if stats_df.empty:
        st.warning("No market data matches the selected filters.")
        st.stop()

    stats = stats_df.iloc[0]

    if int(stats["total_listings"]) == 0:
        st.warning("No market data matches the selected filters.")
        st.stop()

    st.header("Market Analyst Dashboard")
    st.write(
        "Understand the major patterns in the used car market."
    )

    # Show the main market indicators
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Listings",
        f"{int(stats['total_listings']):,}"
    )

    col2.metric(
        "Average Market Price",
        f"₹{stats['average_price']:.2f} L"
    )

    top_brand = plot_brand_listings(
        filters,
        1
    )

    if top_brand.empty:
        top_brand_name = "N/A"
    else:
        top_brand_name = top_brand.iloc[0]["oem"]

    col3.metric(
        "Top Brand",
        str(top_brand_name).title()
    )

    top_city = plot_city_listings(
        filters,
        1
    )

    if top_city.empty:
        top_city_name = "N/A"
    else:
        top_city_name = top_city.iloc[0]["city"]

    col4.metric(
        "Top City",
        str(top_city_name).title()
    )

    # Show which brands dominate the selected market
    st.subheader("Brand Market Distribution")

    brand_data = plot_brand_listings(
        filters
    )

    brand_data = brand_data.sort_values(
        "listings"
    )

    fig, ax = plt.subplots()

    ax.barh(
        brand_data["oem"],
        brand_data["listings"]
    )

    ax.set_xlabel("Number of Listings")
    ax.set_ylabel("Brand")
    ax.set_title("Listings by Brand")

    fig.tight_layout()
    st.pyplot(fig)

    # Show how listings are distributed across cities
    st.subheader("City Market Distribution")

    city_data = plot_city_listings(
        filters
    )

    city_data = city_data.sort_values(
        "listings"
    )

    fig, ax = plt.subplots()

    ax.barh(
        city_data["city"],
        city_data["listings"]
    )

    ax.set_xlabel("Number of Listings")
    ax.set_ylabel("City")
    ax.set_title("Listings by City")

    fig.tight_layout()
    st.pyplot(fig)

    # Compare average used car prices between major cities
    st.subheader("Average Price by City")

    city_price = plot_city_price(
        filters
    )

    city_price = city_price.sort_values(
        "average_price"
    )

    fig, ax = plt.subplots()

    ax.barh(
        city_price["city"],
        city_price["average_price"]
    )

    ax.set_xlabel("Average Price (Lakhs)")
    ax.set_ylabel("City")
    ax.set_title("Average Used Car Price by City")

    fig.tight_layout()
    st.pyplot(fig)

    # Show the distribution of fuel types in the market
    st.subheader("Fuel Distribution")

    fuel_data = plot_fuel_distribution(
        filters
    )

    fig, ax = plt.subplots()

    ax.bar(
        fuel_data["fuel"],
        fuel_data["listings"]
    )

    ax.set_xlabel("Fuel Type")
    ax.set_ylabel("Listings")
    ax.set_title("Fuel Type Distribution")

    fig.tight_layout()
    st.pyplot(fig)

    # Show the relationship between vehicle mileage and price
    st.subheader("Price and Mileage")

    mileage_data = plot_price_vs_mileage(
        filters
    )

    fig, ax = plt.subplots()

    ax.scatter(
        mileage_data["km_thousands"],
        mileage_data["price_lakhs"],
        alpha=0.4
    )

    ax.set_xlabel("Mileage (000 KM)")
    ax.set_ylabel("Price (Lakhs)")
    ax.set_title("Price vs Mileage")

    fig.tight_layout()
    st.pyplot(fig)

    # Show the detailed market data for the selected filters
    st.subheader("Filtered Market Data")

    cars = get_filtered_cars(
        filters,
        500
    )

    if cars.empty:
        st.info("No cars match the selected filters.")
    else:
        st.dataframe(
            cars,
            width="stretch",
            hide_index=True
        )

st.divider()

# Show the technology stack used by the dashboard
st.caption(
    "Used Car Market Analytics | PostgreSQL | Psycopg | Streamlit"
)