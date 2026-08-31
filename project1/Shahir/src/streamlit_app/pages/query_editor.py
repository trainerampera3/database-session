import streamlit as st
import logging
from utils.db_helper import run_qurey

logging.basicConfig(level=logging.INFO)


def show_query_editor():

    st.title("Query Editor")

    query = st.text_area(
        "SQL Query",
        value="SELECT * FROM patients;",
        height=200
    )

    if st.button("Execute"):

        if not query.strip():
            st.warning("Please enter a SQL query.")
            return

        try:
            logging.info("Executing SQL query")

            res = run_qurey(query)

            st.dataframe(
                res,
                use_container_width=True
            )

            logging.info("Query executed successfully")

        except Exception as e:
            logging.error(f"Query execution failed: {e}")

            st.error(f"Query execution failed: {e}")