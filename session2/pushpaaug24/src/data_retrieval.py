import pandas as pd

from database import create_connection


MONTH_ORDER = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}


def build_filters(
    hotel=None,
    year=None,
    month=None,
    customer_type=None,
    market_segment=None,
    booking_status=None
):

    conditions = []
    params = []

    if hotel and hotel != "All Hotels":
        conditions.append("h.hotel = %s")
        params.append(hotel)

    if year and year != "All Years":
        conditions.append(
            "EXTRACT(YEAR FROM b.arrival_date)::INTEGER = %s"
        )
        params.append(year)

    if month and month != "All Months":
        conditions.append(
            "TRIM(TO_CHAR(b.arrival_date, 'Month')) = %s"
        )
        params.append(month)

    if customer_type and customer_type != "All Customer Types":
        conditions.append("c.customer_type = %s")
        params.append(customer_type)

    if market_segment and market_segment != "All Market Segments":
        conditions.append("b.market_segment = %s")
        params.append(market_segment)

    if booking_status and booking_status != "All Booking Status":
        conditions.append("b.booking_status = %s")
        params.append(booking_status)

    if conditions:
        return " AND " + " AND ".join(conditions), params

    return "", params


def get_filter_options(connection):

    result = {}

    queries = {

        "hotels": """
            SELECT DISTINCT hotel
            FROM hotels
            ORDER BY hotel
        """,

        "years": """
            SELECT DISTINCT
                EXTRACT(YEAR FROM arrival_date)::INTEGER AS year
            FROM bookings
            ORDER BY year
        """,

        "customer_types": """
            SELECT DISTINCT customer_type
            FROM customers
            WHERE customer_type IS NOT NULL
            ORDER BY customer_type
        """,

        "market_segments": """
            SELECT DISTINCT market_segment
            FROM bookings
            WHERE market_segment IS NOT NULL
            ORDER BY market_segment
        """,

        "booking_status": """
            SELECT DISTINCT booking_status
            FROM bookings
            WHERE booking_status IS NOT NULL
            ORDER BY booking_status
        """
    }

    for name, query in queries.items():

        result[name] = pd.read_sql_query(
            query,
            connection
        ).iloc[:, 0].tolist()

    result["months"] = list(MONTH_ORDER.keys())

    return result


def get_kpis(
    connection,
    hotel=None,
    year=None,
    month=None,
    customer_type=None,
    market_segment=None,
    booking_status=None
):

    where_sql, params = build_filters(
        hotel,
        year,
        month,
        customer_type,
        market_segment,
        booking_status
    )

    query = f"""
        SELECT

            COUNT(*) AS total_bookings,

            COALESCE(
                SUM(b.total_guests),
                0
            ) AS total_guests,

            COALESCE(
                SUM(b.estimated_revenue),
                0
            ) AS total_revenue,

            COALESCE(
                AVG(b.adr),
                0
            ) AS average_adr,

            COALESCE(
                COUNT(*) FILTER (
                    WHERE b.booking_status = 'Canceled'
                ) * 100.0
                / NULLIF(COUNT(*), 0),
                0
            ) AS cancellation_rate

        FROM bookings b

        JOIN hotels h
            ON b.hotel_id = h.hotel_id

        JOIN customers c
            ON b.customer_id = c.customer_id

        WHERE 1 = 1
        {where_sql}
    """

    return pd.read_sql_query(
        query,
        connection,
        params=params
    ).iloc[0]


def get_monthly_bookings(
    connection,
    hotel=None,
    year=None,
    month=None,
    customer_type=None,
    market_segment=None,
    booking_status=None
):

    where_sql, params = build_filters(
        hotel,
        year,
        month,
        customer_type,
        market_segment,
        booking_status
    )

    query = f"""
        SELECT

            EXTRACT(
                YEAR FROM b.arrival_date
            )::INTEGER AS arrival_date_year,

            TRIM(
                TO_CHAR(
                    b.arrival_date,
                    'Month'
                )
            ) AS arrival_date_month,

            COUNT(*) AS bookings

        FROM bookings b

        JOIN hotels h
            ON b.hotel_id = h.hotel_id

        JOIN customers c
            ON b.customer_id = c.customer_id

        WHERE 1 = 1
        {where_sql}

        GROUP BY
            EXTRACT(YEAR FROM b.arrival_date),
            EXTRACT(MONTH FROM b.arrival_date),
            TRIM(TO_CHAR(b.arrival_date, 'Month'))

        ORDER BY
            EXTRACT(YEAR FROM b.arrival_date),
            EXTRACT(MONTH FROM b.arrival_date)
    """

    df = pd.read_sql_query(
        query,
        connection,
        params=params
    )

    if not df.empty:

        df["month_number"] = (
            df["arrival_date_month"]
            .map(MONTH_ORDER)
        )

        df["month_year"] = (
            df["arrival_date_month"]
            + " "
            + df["arrival_date_year"].astype(str)
        )

    return df


def get_hotel_analysis(
    connection,
    hotel=None,
    year=None,
    month=None,
    customer_type=None,
    market_segment=None,
    booking_status=None
):

    where_sql, params = build_filters(
        hotel,
        year,
        month,
        customer_type,
        market_segment,
        booking_status
    )

    query = f"""
        SELECT

            h.hotel,

            COUNT(*) AS bookings,

            COALESCE(
                SUM(b.total_guests),
                0
            ) AS guests,

            COALESCE(
                SUM(b.estimated_revenue),
                0
            ) AS revenue,

            COALESCE(
                AVG(b.adr),
                0
            ) AS average_adr,

            COALESCE(
                COUNT(*) FILTER (
                    WHERE b.booking_status = 'Canceled'
                ) * 100.0
                / NULLIF(COUNT(*), 0),
                0
            ) AS cancellation_rate

        FROM bookings b

        JOIN hotels h
            ON b.hotel_id = h.hotel_id

        JOIN customers c
            ON b.customer_id = c.customer_id

        WHERE 1 = 1
        {where_sql}

        GROUP BY h.hotel

        ORDER BY bookings DESC
    """

    return pd.read_sql_query(
        query,
        connection,
        params=params
    )


def get_top_countries(
    connection,
    hotel=None,
    year=None,
    month=None,
    customer_type=None,
    market_segment=None,
    booking_status=None
):

    where_sql, params = build_filters(
        hotel,
        year,
        month,
        customer_type,
        market_segment,
        booking_status
    )

    query = f"""
        SELECT

            COALESCE(
                c.country,
                'Unknown'
            ) AS country,

            COUNT(*) AS bookings,

            COALESCE(
                SUM(b.total_guests),
                0
            ) AS guests,

            COALESCE(
                SUM(b.estimated_revenue),
                0
            ) AS revenue

        FROM bookings b

        JOIN hotels h
            ON b.hotel_id = h.hotel_id

        JOIN customers c
            ON b.customer_id = c.customer_id

        WHERE 1 = 1
        {where_sql}

        GROUP BY c.country

        ORDER BY bookings DESC
    """

    return pd.read_sql_query(
        query,
        connection,
        params=params
    )


def get_customer_type_analysis(
    connection,
    hotel=None,
    year=None,
    month=None,
    customer_type=None,
    market_segment=None,
    booking_status=None
):

    where_sql, params = build_filters(
        hotel,
        year,
        month,
        customer_type,
        market_segment,
        booking_status
    )

    query = f"""
        SELECT

            c.customer_type,

            COUNT(*) AS bookings,

            COALESCE(
                AVG(b.total_nights),
                0
            ) AS average_stay,

            COALESCE(
                AVG(b.adr),
                0
            ) AS average_adr,

            COALESCE(
                COUNT(*) FILTER (
                    WHERE b.booking_status = 'Canceled'
                ) * 100.0
                / NULLIF(COUNT(*), 0),
                0
            ) AS cancellation_rate

        FROM bookings b

        JOIN hotels h
            ON b.hotel_id = h.hotel_id

        JOIN customers c
            ON b.customer_id = c.customer_id

        WHERE 1 = 1
        {where_sql}

        GROUP BY c.customer_type

        ORDER BY bookings DESC
    """

    return pd.read_sql_query(
        query,
        connection,
        params=params
    )


def get_repeated_guest_analysis(
    connection,
    hotel=None,
    year=None,
    month=None,
    customer_type=None,
    market_segment=None,
    booking_status=None
):

    where_sql, params = build_filters(
        hotel,
        year,
        month,
        customer_type,
        market_segment,
        booking_status
    )

    query = f"""
        SELECT

            c.is_repeated_guest,

            COUNT(*) AS bookings,

            COALESCE(
                AVG(b.total_nights),
                0
            ) AS average_stay,

            COALESCE(
                AVG(b.adr),
                0
            ) AS average_adr

        FROM bookings b

        JOIN hotels h
            ON b.hotel_id = h.hotel_id

        JOIN customers c
            ON b.customer_id = c.customer_id

        WHERE 1 = 1
        {where_sql}

        GROUP BY c.is_repeated_guest

        ORDER BY c.is_repeated_guest
    """

    df = pd.read_sql_query(
        query,
        connection,
        params=params
    )

    if not df.empty:

        df["guest_category"] = (
            df["is_repeated_guest"]
            .map({
                0: "New Guest",
                1: "Repeated Guest"
            })
        )

    return df


def get_market_segment_analysis(
    connection,
    hotel=None,
    year=None,
    month=None,
    customer_type=None,
    market_segment=None,
    booking_status=None
):

    where_sql, params = build_filters(
        hotel,
        year,
        month,
        customer_type,
        market_segment,
        booking_status
    )

    query = f"""
        SELECT

            b.market_segment,

            COUNT(*) AS bookings,

            COALESCE(
                SUM(b.estimated_revenue),
                0
            ) AS revenue,

            COALESCE(
                AVG(b.adr),
                0
            ) AS average_adr,

            COALESCE(
                COUNT(*) FILTER (
                    WHERE b.booking_status = 'Canceled'
                ) * 100.0
                / NULLIF(COUNT(*), 0),
                0
            ) AS cancellation_rate

        FROM bookings b

        JOIN hotels h
            ON b.hotel_id = h.hotel_id

        JOIN customers c
            ON b.customer_id = c.customer_id

        WHERE 1 = 1
        {where_sql}

        GROUP BY b.market_segment

        ORDER BY bookings DESC
    """

    return pd.read_sql_query(
        query,
        connection,
        params=params
    )


def get_room_type_analysis(
    connection,
    hotel=None,
    year=None,
    month=None,
    customer_type=None,
    market_segment=None,
    booking_status=None
):

    where_sql, params = build_filters(
        hotel,
        year,
        month,
        customer_type,
        market_segment,
        booking_status
    )

    query = f"""
        SELECT

            b.reserved_room_type,

            COUNT(*) AS bookings,

            COALESCE(
                AVG(b.adr),
                0
            ) AS average_adr,

            COALESCE(
                COUNT(*) FILTER (
                    WHERE b.booking_status = 'Canceled'
                ) * 100.0
                / NULLIF(COUNT(*), 0),
                0
            ) AS cancellation_rate

        FROM bookings b

        JOIN hotels h
            ON b.hotel_id = h.hotel_id

        JOIN customers c
            ON b.customer_id = c.customer_id

        WHERE 1 = 1
        {where_sql}

        GROUP BY b.reserved_room_type

        ORDER BY bookings DESC
    """

    return pd.read_sql_query(
        query,
        connection,
        params=params
    )