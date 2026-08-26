from pathlib import Path

import pandas as pd
import psycopg


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def create_connection():
    """Create a PostgreSQL connection."""
    try:
        connection = psycopg.connect(
            host="localhost",
            dbname="postgres",
            user="gajapathi",
            password="admin@123",
        )

        return connection

    except psycopg.Error as error:
        print(f"Connection error: {error}")
        return None




def get_filter_options(connection):
    """
    Retrieve small dimension-table values used by Streamlit
    sidebar filters.

    No fact_table is scanned here.
    """

    queries = {
        "years": """
            SELECT DISTINCT year
            FROM time_dim
            ORDER BY year
        """,

        "quarters": """
            SELECT DISTINCT quarter
            FROM time_dim
            ORDER BY quarter
        """,

        "months": """
            SELECT DISTINCT month
            FROM time_dim
            ORDER BY month
        """,

        "divisions": """
            SELECT DISTINCT division
            FROM store_dim
            ORDER BY division
        """,

        "districts": """
            SELECT DISTINCT district
            FROM store_dim
            ORDER BY district
        """,

        "payment_types": """
            SELECT DISTINCT trans_type
            FROM trans_dim
            ORDER BY trans_type
        """,

        "products": """
            SELECT DISTINCT item_name
            FROM item_dim
            ORDER BY item_name
        """,
    }

    result = {}

    for name, query in queries.items():
        result[name] = pd.read_sql_query(query, connection).iloc[:, 0].tolist()

    return result




def build_filters(
    years=None,
    quarters=None,
    months=None,
    divisions=None,
    districts=None,
    payment_types=None,
    products=None,
):
    """
    Build SQL WHERE conditions and parameters.

    Uses PostgreSQL parameters instead of string interpolation.
    """

    conditions = []
    params = []

    if years:
        conditions.append("t.year = ANY(%s)")
        params.append(years)

    if quarters:
        conditions.append("t.quarter = ANY(%s)")
        params.append(quarters)

    if months:
        conditions.append("t.month = ANY(%s)")
        params.append(months)

    if divisions:
        conditions.append("s.division = ANY(%s)")
        params.append(divisions)

    if districts:
        conditions.append("s.district = ANY(%s)")
        params.append(districts)

    if payment_types:
        conditions.append("p.trans_type = ANY(%s)")
        params.append(payment_types)

    if products:
        conditions.append("i.item_name = ANY(%s)")
        params.append(products)

    if not conditions:
        return "", params

    return " AND " + " AND ".join(conditions), params




BASE_FROM = """
    FROM fact_table f

    JOIN time_dim t
        ON f.time_key = t.time_key

    JOIN store_dim s
        ON f.store_key = s.store_key

    JOIN trans_dim p
        ON f.payment_key = p.payment_key

    JOIN item_dim i
        ON f.item_key = i.item_key
"""




def get_kpis(
    connection,
    years=None,
    quarters=None,
    months=None,
    divisions=None,
    districts=None,
    payment_types=None,
    products=None,
):
    """Retrieve dashboard KPIs directly from PostgreSQL."""

    where_sql, params = build_filters(
        years,
        quarters,
        months,
        divisions,
        districts,
        payment_types,
        products,
    )

    query = f"""
        SELECT
            COALESCE(SUM(f.total_price), 0) AS total_sales,
            COUNT(*) AS total_transactions,
            COALESCE(SUM(f.quantity), 0) AS total_quantity,
            COUNT(DISTINCT f.coustomer_key) AS total_customers
        {BASE_FROM}
        WHERE 1 = 1
        {where_sql}
    """

    return pd.read_sql_query(
        query,
        connection,
        params=params,
    ).iloc[0]




def get_sales_by_year(connection, **filters):

    where_sql, params = build_filters(**filters)

    query = f"""
        SELECT
            t.year,
            SUM(f.total_price) AS total_price
        {BASE_FROM}
        WHERE 1 = 1
        {where_sql}
        GROUP BY t.year
        ORDER BY t.year
    """

    return pd.read_sql_query(
        query,
        connection,
        params=params,
    )




def get_monthly_sales(connection, **filters):

    where_sql, params = build_filters(**filters)

    query = f"""
        SELECT
            t.month,
            SUM(f.total_price) AS total_price
        {BASE_FROM}
        WHERE 1 = 1
        {where_sql}
        GROUP BY t.month
        ORDER BY t.month
    """

    return pd.read_sql_query(
        query,
        connection,
        params=params,
    )



def get_payment_sales(connection, **filters):

    where_sql, params = build_filters(**filters)

    query = f"""
        SELECT
            p.trans_type,
            SUM(f.total_price) AS total_price
        {BASE_FROM}
        WHERE 1 = 1
        {where_sql}
        GROUP BY p.trans_type
        ORDER BY total_price DESC
    """

    return pd.read_sql_query(
        query,
        connection,
        params=params,
    )




def get_division_sales(connection, **filters):

    where_sql, params = build_filters(**filters)

    query = f"""
        SELECT
            s.division,
            SUM(f.total_price) AS total_price
        {BASE_FROM}
        WHERE 1 = 1
        {where_sql}
        GROUP BY s.division
        ORDER BY total_price DESC
    """

    return pd.read_sql_query(
        query,
        connection,
        params=params,
    )




def get_top_products(connection, **filters):

    where_sql, params = build_filters(**filters)

    query = f"""
        SELECT
            i.item_name,
            SUM(f.total_price) AS total_price
        {BASE_FROM}
        WHERE 1 = 1
        {where_sql}
        GROUP BY i.item_name
        ORDER BY total_price DESC
        LIMIT 10
    """

    return pd.read_sql_query(
        query,
        connection,
        params=params,
    )




def get_product_quantity(connection, **filters):

    where_sql, params = build_filters(**filters)

    query = f"""
        SELECT
            i.item_name,
            SUM(f.quantity) AS quantity
        {BASE_FROM}
        WHERE 1 = 1
        {where_sql}
        GROUP BY i.item_name
        ORDER BY quantity DESC
        LIMIT 10
    """

    return pd.read_sql_query(
        query,
        connection,
        params=params,
    )



def get_district_sales(connection, **filters):

    where_sql, params = build_filters(**filters)

    query = f"""
        SELECT
            s.district,
            SUM(f.total_price) AS total_price
        {BASE_FROM}
        WHERE 1 = 1
        {where_sql}
        GROUP BY s.district
        ORDER BY total_price DESC
        LIMIT 10
    """

    return pd.read_sql_query(
        query,
        connection,
        params=params,
    )




def get_district_transactions(connection, **filters):

    where_sql, params = build_filters(**filters)

    query = f"""
        SELECT
            s.district,
            COUNT(*) AS transactions
        {BASE_FROM}
        WHERE 1 = 1
        {where_sql}
        GROUP BY s.district
        ORDER BY transactions DESC
        LIMIT 10
    """

    return pd.read_sql_query(
        query,
        connection,
        params=params,
    )



def get_top_product(connection, **filters):

    df = get_top_products(connection, **filters)

    if df.empty:
        return None, 0

    return df.iloc[0]["item_name"], df.iloc[0]["total_price"]


def get_top_division(connection, **filters):

    df = get_division_sales(connection, **filters)

    if df.empty:
        return None, 0

    return df.iloc[0]["division"], df.iloc[0]["total_price"]


def get_top_district(connection, **filters):

    df = get_district_sales(connection, **filters)

    if df.empty:
        return None, 0

    return df.iloc[0]["district"], df.iloc[0]["total_price"]


def get_leading_payment(connection, **filters):

    df = get_payment_sales(connection, **filters)

    if df.empty:
        return None, 0

    total = df["total_price"].sum()

    share = (
        df.iloc[0]["total_price"] / total * 100
        if total
        else 0
    )

    return df.iloc[0]["trans_type"], share