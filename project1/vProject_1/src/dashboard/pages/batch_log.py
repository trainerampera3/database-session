import pandas as pd
import streamlit as st


# Load overall batch statistics.
def load_batch_statistics(connection):
    query = """
        SELECT
            COUNT(*) AS batches,
            COALESCE(
                SUM(rows_inserted),
                0
            ) AS rows_inserted,
            COALESCE(
                SUM(rows_rejected),
                0
            ) AS rows_rejected,
            CASE
                WHEN COALESCE(
                    SUM(rows_processed),
                    0
                ) = 0
                THEN 0
                ELSE ROUND(
                    SUM(rows_inserted)::NUMERIC
                    /
                    SUM(rows_processed)::NUMERIC
                    * 100,
                    2
                )
            END AS success_rate
        FROM business_location.batch_log;
    """

    return pd.read_sql_query(
        query,
        connection
    )


# Load batch records.
def load_batch_logs(connection):
    query = """
        SELECT
            batch_number AS "Batch",
            source_file AS "Source file",
            target_table AS "Target",
            stage AS "Stage",
            rows_processed AS "Rows",
            rows_inserted AS "Inserted",
            rows_rejected AS "Rejected",
            duration_seconds AS "Duration",
            status AS "Status",
            started_at AS "Started",
            completed_at AS "Completed",
            error_message AS "Error"
        FROM business_location.batch_log
        ORDER BY started_at DESC;
    """

    return pd.read_sql_query(
        query,
        connection
    )


# Load batch statistics grouped by target table.
def load_table_batch_statistics(connection):
    query = """
        SELECT
            target_table AS "Target table",
            COUNT(*) AS "Batches",
            SUM(rows_processed) AS "Rows processed",
            SUM(rows_inserted) AS "Rows inserted",
            SUM(rows_rejected) AS "Rows rejected",
            ROUND(
                SUM(duration_seconds)::NUMERIC,
                2
            ) AS "Duration seconds"
        FROM business_location.batch_log
        GROUP BY target_table
        ORDER BY target_table;
    """

    return pd.read_sql_query(
        query,
        connection
    )


# Render the batch process log.
def render_batch_log(connection):
    st.markdown(
        "### Batch process log"
    )

    statistics = load_batch_statistics(
        connection
    )

    if statistics.empty:
        st.info(
            "No migration batches have been recorded yet."
        )
        return

    row = statistics.iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Batches",
            f"{int(row['batches']):,}"
        )

    with col2:
        st.metric(
            "Rows inserted",
            f"{int(row['rows_inserted']):,}"
        )

    with col3:
        st.metric(
            "Rows rejected",
            f"{int(row['rows_rejected']):,}"
        )

    with col4:
        st.metric(
            "Success rate",
            f"{float(row['success_rate']):.2f}%"
        )

    st.markdown(
        "### Batches by table"
    )

    table_statistics = (
        load_table_batch_statistics(
            connection
        )
    )

    st.dataframe(
        table_statistics,
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        "### Runs"
    )

    status_filter = st.radio(
        "Status",
        [
            "All",
            "Succeeded",
            "Partial",
            "Failed"
        ],
        horizontal=True
    )

    logs = load_batch_logs(
        connection
    )

    if status_filter != "All":
        logs = logs[
            logs["Status"] == status_filter
        ]

    st.dataframe(
        logs,
        use_container_width=True,
        hide_index=True
    )