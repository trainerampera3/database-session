import psycopg as pg
import streamlit as st



st.set_page_config(
    page_title="Data Migration Tool",
    layout="wide"
)
st.title('Ampera')
if "failed" not in st.session_state:
    st.session_state.failed = 0

if "success" not in st.session_state:
    st.session_state.success = 0

pages = {
    "Main": [
        st.Page(
            "pages/dashboard.py",
            title="Dashboard",
        ),
        st.Page(
            "pages/upload.py",
            title="Upload",
        ),
        st.Page(
            "pages/query.py",
            title="Query",
        ),
        st.Page('pages/batch_log.py', title='Batch Log')
    ]
}

pg = st.navigation(pages)

pg.run()