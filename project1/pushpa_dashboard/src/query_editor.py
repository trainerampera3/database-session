import time
import pandas as pd
import streamlit as st

from db import get_connection


def execute_query(query):
    start = time.perf_counter()

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(query)

            if cur.description:
                columns = [column.name for column in cur.description]
                rows = cur.fetchall()

                result = pd.DataFrame(
                    rows,
                    columns=columns
                )
            else:
                conn.commit()
                result = pd.DataFrame()

        elapsed = time.perf_counter() - start

        return result, elapsed

    finally:
        conn.close()


def show_query_result(result, elapsed):

    st.subheader("Query Result")

    st.caption(
        f"{len(result):,} rows · {elapsed:.2f} s"
    )

    with st.container(border=True):

        if result.empty:

            st.info(
                "Query executed successfully. No rows returned."
            )

        else:

            display_df = result.copy()

            display_df.insert(
                0,
                "#",
                range(1, len(display_df) + 1)
            )

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=500
            )


def query_section(title, default_query, key):

    title_col, button_col = st.columns([8, 2])

    with title_col:
        st.subheader(title)

    with button_col:

        run_query = st.button(
            "▶ Run Query",
            key=f"run_{key}",
            use_container_width=True
        )

    query = st.text_area(
        "SQL Query",
        value=default_query.strip(),
        height=300,
        key=f"sql_{key}"
    )

    if run_query:

        if not query.strip():

            st.warning("Please enter a SQL query.")

        else:

            try:

                result, elapsed = execute_query(query)

                st.session_state[f"result_{key}"] = result
                st.session_state[f"time_{key}"] = elapsed

                st.success(
                    "Query executed successfully."
                )

            except Exception as error:

                st.error(
                    f"Query failed: {error}"
                )

    result_key = f"result_{key}"
    time_key = f"time_{key}"

    if result_key in st.session_state:

        show_query_result(
            st.session_state[result_key],
            st.session_state[time_key]
        )


def show_query_editor():

    st.header("Query Editor")

    st.write(
        "Explore railway data using dynamic PostgreSQL queries."
    )

    st.divider()

    tabs = st.tabs([
        "Train Overview",
        "Route Analysis",
        "Station Analysis",
        "Class Analysis",
        "Custom SQL"
    ])

    with tabs[0]:

        query_section(
            "Train Overview",
            """
SELECT
    train_no,
    station_code,
    station_name,
    route_number,
    arrival_time,
    departure_time,
    distance
FROM train_schedule
ORDER BY train_no
LIMIT 20;
            """,
            "train_overview"
        )

    with tabs[1]:

        query_section(
            "Route Analysis",
            """
SELECT
    train_no,
    COUNT(*) AS station_count,
    MAX(route_number) AS route_count,
    MAX(distance) AS maximum_distance
FROM train_schedule
GROUP BY train_no
ORDER BY maximum_distance DESC
LIMIT 20;
            """,
            "route_analysis"
        )

    with tabs[2]:

        query_section(
            "Station Analysis",
            """
SELECT
    station_code,
    station_name,
    COUNT(DISTINCT train_no) AS train_count,
    ROUND(AVG(distance)::numeric, 2) AS average_distance,
    MAX(distance) AS maximum_distance
FROM train_schedule
GROUP BY
    station_code,
    station_name
ORDER BY train_count DESC
LIMIT 20;
            """,
            "station_analysis"
        )

    with tabs[3]:

        query_section(
            "Class Analysis",
            """
SELECT
    train_no,
    MAX("1A") AS class_1a,
    MAX("2A") AS class_2a,
    MAX("3A") AS class_3a,
    MAX("SL") AS class_sl
FROM train_schedule
GROUP BY train_no
ORDER BY train_no
LIMIT 20;
            """,
            "class_analysis"
        )

    with tabs[4]:

        query_section(
            "Custom SQL",
            """
SELECT
    train_no,
    station_code,
    station_name,
    route_number,
    arrival_time,
    departure_time,
    distance
FROM train_schedule
LIMIT 20;
            """,
            "custom_sql"
        )