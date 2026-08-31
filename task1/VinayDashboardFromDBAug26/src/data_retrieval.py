import pandas as pd
from db_connection import get_connection

# Execute a SELECT query and return the result as a DataFrame
def execute_query(query, params=None):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            rows = cur.fetchall()
            columns = [desc.name for desc in cur.description]

        return pd.DataFrame(rows, columns=columns)
    finally:
        conn.close()


# Add the selected dashboard filters to the SQL query
def apply_filters(query, params, filters=None, exclude_filter=None):
    if not filters:
        return query, params

    filter_mapping = {
        "brand": "oem",
        "fuel": "fuel",
        "transmission": "transmission",
        "city": "city",
        "state": "state",
        "body": "body",
        "owner_type": "owner_type",
        "price_segment": "price_segment",
        "model": "model"
    }

    for filter_name, column in filter_mapping.items():
        if filter_name == exclude_filter:
            continue

        value = filters.get(filter_name)

        if value is None or value == "All":
            continue

        query += f" AND {column} = %s"
        params.append(value)

    return query, params


# Get distinct values for a particular dashboard filter
def get_distinct_values(column, filters=None, exclude_filter=None):
    allowed_columns = [
        "oem",
        "fuel",
        "transmission",
        "city",
        "state",
        "body",
        "owner_type",
        "price_segment",
        "model"
    ]

    if column not in allowed_columns:
        raise ValueError("Invalid column")

    query = f"""
        SELECT DISTINCT {column}
        FROM market_data
        WHERE {column} IS NOT NULL
    """

    params = []

    # Apply the other selected filters to make the options dependent
    query, params = apply_filters(
        query,
        params,
        filters,
        exclude_filter
    )

    query += f" ORDER BY {column}"

    df = execute_query(query, params)

    return df[column].tolist()


# Return only the filters needed for the selected dashboard perspective
def get_filter_options(filters=None, perspective="Customer"):
    options = {}

    if perspective == "Customer":
        options["brand"] = get_distinct_values(
            "oem",
            filters,
            "brand"
        )

        options["model"] = get_distinct_values(
            "model",
            filters,
            "model"
        )

        options["price_segment"] = get_distinct_values(
            "price_segment",
            filters,
            "price_segment"
        )

        options["fuel"] = get_distinct_values(
            "fuel",
            filters,
            "fuel"
        )

        options["transmission"] = get_distinct_values(
            "transmission",
            filters,
            "transmission"
        )

        options["body"] = get_distinct_values(
            "body",
            filters,
            "body"
        )

        options["city"] = get_distinct_values(
            "city",
            filters,
            "city"
        )

    elif perspective == "Seller / Dealer":
        options["city"] = get_distinct_values(
            "city",
            filters,
            "city"
        )

        options["brand"] = get_distinct_values(
            "oem",
            filters,
            "brand"
        )

        options["model"] = get_distinct_values(
            "model",
            filters,
            "model"
        )

        options["price_segment"] = get_distinct_values(
            "price_segment",
            filters,
            "price_segment"
        )

        options["fuel"] = get_distinct_values(
            "fuel",
            filters,
            "fuel"
        )

        options["body"] = get_distinct_values(
            "body",
            filters,
            "body"
        )

    else:
        options["state"] = get_distinct_values(
            "state",
            filters,
            "state"
        )

        options["city"] = get_distinct_values(
            "city",
            filters,
            "city"
        )

        options["brand"] = get_distinct_values(
            "oem",
            filters,
            "brand"
        )

        options["fuel"] = get_distinct_values(
            "fuel",
            filters,
            "fuel"
        )

        options["transmission"] = get_distinct_values(
            "transmission",
            filters,
            "transmission"
        )

        options["body"] = get_distinct_values(
            "body",
            filters,
            "body"
        )

        options["price_segment"] = get_distinct_values(
            "price_segment",
            filters,
            "price_segment"
        )

    return options


# Get the main statistics for the currently selected filters
def basic_statistics(filters=None):
    query = """
        SELECT
            COUNT(*) AS total_listings,
            AVG(price_lakhs) AS average_price,
            MIN(price_lakhs) AS lowest_price,
            MAX(price_lakhs) AS highest_price,
            AVG(km_thousands) AS average_mileage,
            AVG(vehicle_age) AS average_vehicle_age
        FROM market_data
        WHERE 1 = 1
    """

    params = []

    query, params = apply_filters(
        query,
        params,
        filters
    )

    return execute_query(query, params)


# Get prices used for the customer price distribution chart
def plot_price_distribution(filters=None):
    query = """
        SELECT price_lakhs
        FROM market_data
        WHERE price_lakhs IS NOT NULL
    """

    params = []

    query, params = apply_filters(
        query,
        params,
        filters
    )

    return execute_query(query, params)


# Get average prices for the most listed models
def plot_price_by_model(filters=None, top_n=10):
    query = """
        SELECT
            model,
            AVG(price_lakhs) AS average_price,
            COUNT(*) AS listings
        FROM market_data
        WHERE model IS NOT NULL
    """

    params = []

    query, params = apply_filters(
        query,
        params,
        filters
    )

    query += """
        GROUP BY model
        ORDER BY average_price DESC
        LIMIT %s
    """

    params.append(top_n)

    return execute_query(query, params)


# Get mileage and price values for the relationship chart
def plot_price_vs_mileage(filters=None):
    query = """
        SELECT
            km_thousands,
            price_lakhs
        FROM market_data
        WHERE km_thousands IS NOT NULL
        AND price_lakhs IS NOT NULL
    """

    params = []

    query, params = apply_filters(
        query,
        params,
        filters
    )

    return execute_query(query, params)


# Compare selected models using price, mileage and age
def plot_car_comparison(filters=None, models=None):
    if not models:
        return pd.DataFrame()

    placeholders = ", ".join(["%s"] * len(models))

    query = f"""
        SELECT
            model,
            COUNT(*) AS listings,
            AVG(price_lakhs) AS average_price,
            MIN(price_lakhs) AS minimum_price,
            MAX(price_lakhs) AS maximum_price,
            AVG(km_thousands) AS average_mileage,
            AVG(vehicle_age) AS average_age
        FROM market_data
        WHERE model IN ({placeholders})
    """

    params = list(models)

    query, params = apply_filters(
        query,
        params,
        filters,
        "model"
    )

    query += """
        GROUP BY model
        ORDER BY average_price
    """

    return execute_query(query, params)


# Get the brands with the highest number of listings
def plot_brand_listings(filters=None, top_n=10):
    query = """
        SELECT
            oem,
            COUNT(*) AS listings
        FROM market_data
        WHERE oem IS NOT NULL
    """

    params = []

    query, params = apply_filters(
        query,
        params,
        filters
    )

    query += """
        GROUP BY oem
        ORDER BY listings DESC
        LIMIT %s
    """

    params.append(top_n)

    return execute_query(query, params)


# Get the models with the highest number of listings
def plot_model_listings(filters=None, top_n=10):
    query = """
        SELECT
            model,
            COUNT(*) AS listings
        FROM market_data
        WHERE model IS NOT NULL
    """

    params = []

    query, params = apply_filters(
        query,
        params,
        filters
    )

    query += """
        GROUP BY model
        ORDER BY listings DESC
        LIMIT %s
    """

    params.append(top_n)

    return execute_query(query, params)


# Get average price and listing count for each brand
def plot_brand_price(filters=None, top_n=10):
    query = """
        SELECT
            oem,
            AVG(price_lakhs) AS average_price,
            COUNT(*) AS listings
        FROM market_data
        WHERE oem IS NOT NULL
    """

    params = []

    query, params = apply_filters(
        query,
        params,
        filters
    )

    query += """
        GROUP BY oem
        ORDER BY listings DESC
        LIMIT %s
    """

    params.append(top_n)

    return execute_query(query, params)


# Get average price and listing count for each model
def plot_model_price(filters=None, top_n=10):
    query = """
        SELECT
            model,
            AVG(price_lakhs) AS average_price,
            COUNT(*) AS listings
        FROM market_data
        WHERE model IS NOT NULL
    """

    params = []

    query, params = apply_filters(
        query,
        params,
        filters
    )

    query += """
        GROUP BY model
        ORDER BY listings DESC
        LIMIT %s
    """

    params.append(top_n)

    return execute_query(query, params)


# Get the number of listings in each price segment
def plot_price_segments(filters=None):
    query = """
        SELECT
            price_segment,
            COUNT(*) AS listings
        FROM market_data
        WHERE price_segment IS NOT NULL
    """

    params = []

    query, params = apply_filters(
        query,
        params,
        filters
    )

    query += """
        GROUP BY price_segment
        ORDER BY listings DESC
    """

    return execute_query(query, params)


# Get the cities with the highest number of listings
def plot_city_listings(filters=None, top_n=10):
    query = """
        SELECT
            city,
            COUNT(*) AS listings
        FROM market_data
        WHERE city IS NOT NULL
    """

    params = []

    query, params = apply_filters(
        query,
        params,
        filters
    )

    query += """
        GROUP BY city
        ORDER BY listings DESC
        LIMIT %s
    """

    params.append(top_n)

    return execute_query(query, params)


# Get the average used car price for each city
def plot_city_price(filters=None, top_n=10):
    query = """
        SELECT
            city,
            AVG(price_lakhs) AS average_price,
            COUNT(*) AS listings
        FROM market_data
        WHERE city IS NOT NULL
    """

    params = []

    query, params = apply_filters(
        query,
        params,
        filters
    )

    query += """
        GROUP BY city
        ORDER BY listings DESC
        LIMIT %s
    """

    params.append(top_n)

    return execute_query(query, params)


# Get the number of listings for each fuel type
def plot_fuel_distribution(filters=None):
    query = """
        SELECT
            fuel,
            COUNT(*) AS listings
        FROM market_data
        WHERE fuel IS NOT NULL
    """

    params = []

    query, params = apply_filters(
        query,
        params,
        filters
    )

    query += """
        GROUP BY fuel
        ORDER BY listings DESC
    """

    return execute_query(query, params)


# Get a comparison table for the models selected by the customer
def get_customer_comparison(filters=None, models=None):
    if not models:
        return pd.DataFrame()

    placeholders = ", ".join(["%s"] * len(models))

    query = f"""
        SELECT
            model,
            COUNT(*) AS listings,
            AVG(price_lakhs) AS average_price,
            MIN(price_lakhs) AS minimum_price,
            MAX(price_lakhs) AS maximum_price,
            AVG(km_thousands) AS average_mileage,
            AVG(vehicle_age) AS average_age
        FROM market_data
        WHERE model IN ({placeholders})
    """

    params = list(models)

    query, params = apply_filters(
        query,
        params,
        filters,
        "model"
    )

    query += """
        GROUP BY model
        ORDER BY average_price
    """

    return execute_query(query, params)


# Get detailed vehicle information for the filtered table
def get_filtered_cars(filters=None, limit=500):
    query = """
        SELECT
            u.usedcarskuid,
            u.oem,
            u.model,
            u.variant,
            u.myear,
            u.body,
            u.fuel,
            u.transmission,
            u.km,
            u.owner_type,
            u.city,
            u.state,
            u.utype,
            u.listed_price,
            u.color,
            u.vehicle_age,
            u.price_segment
        FROM used_cars u
        WHERE 1 = 1
    """

    params = []

    query, params = apply_filters(
        query,
        params,
        filters
    )

    query += """
        ORDER BY u.listed_price DESC
        LIMIT %s
    """

    params.append(limit)

    return execute_query(query, params)


# Join market data with technical vehicle specifications
def get_vehicle_specs(filters=None, limit=100):
    query = """
        SELECT
            m.usedcarskuid,
            m.oem,
            m.model,
            m.price_lakhs,
            m.km_thousands,
            m.vehicle_age,
            v.max_torque_delivered,
            v.seats,
            v.max_power_delivered,
            v.no_of_cylinder,
            v.turbo_charger,
            v.super_charger,
            v.length,
            v.width,
            v.height,
            v.wheel_base,
            v.engine_type,
            v.gear_box,
            v.drive_type
        FROM market_data m
        LEFT JOIN vehicle_specs v
        ON m.usedcarskuid = v.usedcarskuid
        WHERE 1 = 1
    """

    params = []

    query, params = apply_filters(
        query,
        params,
        filters
    )

    query += """
        ORDER BY m.price_lakhs
        LIMIT %s
    """

    params.append(limit)

    return execute_query(query, params)