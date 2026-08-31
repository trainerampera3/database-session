import streamlit as st
import pandas as pd

from db import get_connection


# ============================================================
# LOAD DASHBOARD DATA
# ============================================================

def load_dashboard_data():

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            # Total trains
            cur.execute("""
                SELECT COUNT(DISTINCT train_no)
                FROM train_schedule;
            """)
            total_trains = cur.fetchone()[0] or 0

            # Total routes
            cur.execute("""
                SELECT COUNT(DISTINCT route_number)
                FROM train_schedule;
            """)
            total_routes = cur.fetchone()[0] or 0

            # Total stations
            cur.execute("""
                SELECT COUNT(DISTINCT station_code)
                FROM train_schedule;
            """)
            total_stations = cur.fetchone()[0] or 0

            # Total schedules
            cur.execute("""
                SELECT COUNT(*)
                FROM train_schedule;
            """)
            total_schedules = cur.fetchone()[0] or 0

            # All trains
            cur.execute("""
                SELECT DISTINCT train_no
                FROM train_schedule
                ORDER BY train_no;
            """)

            all_trains = [
                row[0]
                for row in cur.fetchall()
            ]

            # All stations
            cur.execute("""
                SELECT DISTINCT
                    station_code,
                    station_name
                FROM train_schedule
                ORDER BY station_code;
            """)

            station_rows = cur.fetchall()

            station_options = {
                row[0]: row[1]
                for row in station_rows
            }

            # Train chart
            cur.execute("""
                SELECT
                    train_no,
                    COUNT(*) AS station_count,
                    MAX(distance) AS total_distance
                FROM train_schedule
                GROUP BY train_no
                ORDER BY total_distance DESC
                LIMIT 10;
            """)

            train_df = pd.DataFrame(
                cur.fetchall(),
                columns=[
                    "Train No",
                    "Station Count",
                    "Total Distance"
                ]
            )

            # Station chart
            cur.execute("""
                SELECT
                    station_code,
                    station_name,
                    COUNT(DISTINCT train_no) AS train_count
                FROM train_schedule
                GROUP BY
                    station_code,
                    station_name
                ORDER BY train_count DESC
                LIMIT 10;
            """)

            station_df = pd.DataFrame(
                cur.fetchall(),
                columns=[
                    "Station Code",
                    "Station Name",
                    "Train Count"
                ]
            )

            return (
                total_trains,
                total_routes,
                total_stations,
                total_schedules,
                all_trains,
                station_options,
                train_df,
                station_df
            )

    finally:

        conn.close()


# ============================================================
# LOAD STATIONS FOR SELECTED TRAINS
# ============================================================

def load_stations_for_trains(selected_trains):

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            if not selected_trains:

                cur.execute("""
                    SELECT DISTINCT
                        station_code,
                        station_name
                    FROM train_schedule
                    ORDER BY station_code;
                """)

                rows = cur.fetchall()

            else:

                placeholders = ", ".join(
                    ["%s"] * len(selected_trains)
                )

                cur.execute(
                    f"""
                    SELECT DISTINCT
                        station_code,
                        station_name
                    FROM train_schedule
                    WHERE train_no IN ({placeholders})
                    ORDER BY station_code;
                    """,
                    selected_trains
                )

                rows = cur.fetchall()

            return {
                row[0]: row[1]
                for row in rows
            }

    finally:

        conn.close()



# LOAD FILTERED SCHEDULE DATA


def load_filtered_schedule(
    selected_trains,
    selected_stations
):

    conn = get_connection()

    try:

        conditions = []
        values = []

        # Train filter
        if selected_trains:

            placeholders = ", ".join(
                ["%s"] * len(selected_trains)
            )

            conditions.append(
                f"train_no IN ({placeholders})"
            )

            values.extend(selected_trains)

        # Station filter
        if selected_stations:

            placeholders = ", ".join(
                ["%s"] * len(selected_stations)
            )

            conditions.append(
                f"station_code IN ({placeholders})"
            )

            values.extend(selected_stations)

        query = """
            SELECT
                train_no,
                station_code,
                station_name,
                route_number,
                arrival_time,
                departure_time,
                distance
            FROM train_schedule
        """

        if conditions:

            query += (
                " WHERE "
                + " AND ".join(conditions)
            )

        query += """
            ORDER BY
                train_no,
                route_number,
                station_code;
        """

        with conn.cursor() as cur:

            cur.execute(
                query,
                values
            )

            rows = cur.fetchall()

            columns = [
                column.name
                for column in cur.description
            ]

        return pd.DataFrame(
            rows,
            columns=columns
        )

    finally:

        conn.close()



# DASHBOARD

def show_dashboard():

    
    # HEADER
    

    st.header(
        "Railway Operations Overview"
    )

    st.write(
        "Monitor trains, routes, stations, and schedule activity "
        "in one place."
    )

    
    # LOAD DASHBOARD DATA
    

    try:

        (
            total_trains,
            total_routes,
            total_stations,
            total_schedules,
            all_trains,
            station_options,
            train_df,
            station_df

        ) = load_dashboard_data()

    except Exception as error:

        st.error(
            f"Unable to load dashboard data: {error}"
        )

        return


    
    

    st.subheader("Filters")

    filter1, filter2 = st.columns(2)


   

    with filter1:

        train_choices = [
            "All"
        ] + all_trains

        selected_train_values = st.multiselect(
            "Train",
            options=train_choices,
            format_func=lambda x: str(x),
            placeholder="Select trains",
            key="dashboard_train_filter"
        )

        # All means no train restriction
        if "All" in selected_train_values:

            selected_trains = []

        else:

            selected_trains = selected_train_values


   

    current_station_options = load_stations_for_trains(
        selected_trains
    )

    with filter2:

        station_choices = [
            "All"
        ] + list(
            current_station_options.keys()
        )

        selected_station_values = st.multiselect(
            "Station",
            options=station_choices,
            format_func=lambda x: (
                "All"
                if x == "All"
                else (
                    f"{x} — "
                    f"{current_station_options[x]}"
                )
            ),
            placeholder="Select stations",
            key="dashboard_station_filter"
        )

        # All means no station restriction
        if "All" in selected_station_values:

            selected_stations = []

        else:

            selected_stations = (
                selected_station_values
            )


   
    # KPI CARDS
   
    st.subheader("Railway Overview")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:

        st.metric(
            "Total Trains",
            f"{total_trains:,}"
        )

    with kpi2:

        st.metric(
            "Total Routes",
            f"{total_routes:,}"
        )

    with kpi3:

        st.metric(
            "Total Stations",
            f"{total_stations:,}"
        )

    with kpi4:

        st.metric(
            "Total Schedules",
            f"{total_schedules:,}"
        )


   
    # CHARTS
    

    chart1, chart2 = st.columns(2)


    # --------------------------------------------------------
    # TRAIN DISTANCE
    # --------------------------------------------------------

    with chart1:

        st.subheader(
            "Train Distance Analysis"
        )

        if not train_df.empty:

            chart_data = (
                train_df
                .set_index("Train No")
                [["Total Distance"]]
            )

            st.bar_chart(
                chart_data,
                height=320
            )

        else:

            st.info(
                "No train data available."
            )


    # --------------------------------------------------------
    # STATION ACTIVITY
    # --------------------------------------------------------

    with chart2:

        st.subheader(
            "Station Activity"
        )

        if not station_df.empty:

            chart_data = (
                station_df
                .set_index("Station Code")
                [["Train Count"]]
            )

            st.bar_chart(
                chart_data,
                height=320
            )

        else:

            st.info(
                "No station data available."
            )


    
    # MAIN SCHEDULE TABLE
   

    st.divider()

    st.subheader(
        "Railway Schedule Overview"
    )

    try:

        schedule_df = load_filtered_schedule(
            selected_trains,
            selected_stations
        )

    except Exception as error:

        st.error(
            f"Unable to load schedule data: {error}"
        )

        return


    # --------------------------------------------------------
    # DISPLAY TABLE
    # --------------------------------------------------------

    if not schedule_df.empty:

        display_df = schedule_df.copy()

        display_df.insert(
            0,
            "#",
            range(
                1,
                len(display_df) + 1
            )
        )

        st.caption(
            f"{len(display_df):,} matching records"
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=500
        )

    else:

        if selected_trains or selected_stations:

            st.info(
                "No schedule records match the selected filters."
            )

        else:

            st.info(
                "No schedule data available."
            )