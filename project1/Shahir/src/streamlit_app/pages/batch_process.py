import streamlit as st
import logging
from utils.database_connection import connection
from utils.db_helper import get_runs_details,get_log_details
logging.basicConfig(level=logging.INFO)


def show_batch_process():

    st.title("Batch Process")

    conn = connection()

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(rows_count), 0),COALESCE(SUM(total_rows), 0)
            FROM runs where status='Done';
        """)

        no_of_batches, rows_count,processed_rows = cursor.fetchone()

    rejected = 0
    if processed_rows is None:
        processed_rows = 0
    rejected=rows_count-processed_rows

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Batches", no_of_batches)

    with col2:
        st.metric("Total Rows Ingested", rows_count)

    with col3:
        st.metric("Rejected",   rejected)

    with col4:
        total_rows = rows_count +  rejected

        if total_rows > 0:
            rate = round((rows_count / total_rows) * 100, 2)
        else:
            rate = 0

        st.metric("Success Rate", f"{rate}%")

    dataframe = get_runs_details()
    logs=get_log_details()
    st.title('Data Migration Status')
    st.dataframe(dataframe, use_container_width=True)
    st.title('Logs')
    st.dataframe(logs,use_container_width=True)