import streamlit as st
from batch_log import get_batch_logs
from upload_page import show_upload_data
from query_editor import show_query_editor
from dashboard import show_dashboard
import streamlit as st



def load_theme():
    with open("theme.css", "r", encoding="utf-8") as css_file:
        st.markdown(
            f"<style>{css_file.read()}</style>",
            unsafe_allow_html=True
        )

load_theme()
st.set_page_config(
    page_title="IRCTC Railway Analytics",
    layout="wide"
)


# ---------- Main Navigation Style ----------

st.markdown("""
<style>

.main-navigation {
    display: flex;
    gap: 18px;
    margin: 20px 0 30px 0;
}

.main-navigation button {
    min-height: 52px;
    border-radius: 8px;
    font-size: 18px;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)


# ---------- Session State ----------

if "main_page" not in st.session_state:
    st.session_state.main_page = "Dashboard"


# ---------- Title ----------

st.title(" IRCTC RAILWAY ANALYTICS")


# ---------- Main Navigation ----------

main_pages = [
    "Dashboard",
    "Upload Data",
    "Query Editor",
    "Batch Log"
]

main_columns = st.columns(4)


for i, page in enumerate(main_pages):

    with main_columns[i]:

        if st.session_state.main_page == page:

            st.markdown(
                """
                <style>
                div[data-testid="stButton"] button {
                    background-color: #d62828;
                    color: white;
                    border: 1px solid #d62828;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

        if st.button(
            page,
            key=f"main_page_{i}",
            use_container_width=True
        ):

            st.session_state.main_page = page

            st.rerun()


st.divider()


# ---------- Pages ----------

if st.session_state.main_page == "Dashboard":

    show_dashboard()

elif st.session_state.main_page == "Upload Data":

    show_upload_data()


elif st.session_state.main_page == "Query Editor":

    show_query_editor()


# elif st.session_state.main_page == "Batch Log":

#     st.header("Batch Log")

#     st.write(
#         "Create and execute SQL queries."
#     )


# elif st.session_state.main_page == "Batch Log":

#     st.header("Batch Log")

#     st.write(
#         "View data processing and migration activity."
#     )

# # elif st.session_state.main_page == "Query Editor":

# #     st.header("Query Editor")

# #     st.write(
# #         "Create and execute SQL queries.
#     )"
elif st.session_state.main_page == "Query Editor":

    show_query_editor()


elif st.session_state.main_page == "Batch Log":

    st.header("Batch  Process Log")

    st.write(
        "Track railway data migration batches and their status."
    )

    logs = get_batch_logs()

    if not logs:

        st.info("No migration batches recorded yet.")

    else:

        for log in logs:

            col1, col2, col3, col4, col5, col6 = st.columns(6)

            with col1:
                st.caption("BATCH ID")
                st.write(logs.index(log) + 1)

            with col2:
                st.caption("START TIME")
                st.write(log.get("start_time", "-"))

            with col3:
                st.caption("END TIME")
                st.write(log.get("end_time", "-"))

            with col4:
                st.caption("FILES")
                st.write(log.get("files", "-"))

            with col5:
                st.caption("ROWS")
                st.write(
                    f'{log.get("total_rows", 0):,}'
                )

            with col6:
                st.caption("STATUS")
                st.success(
                    f'✓ {log.get("status", "-")}'
                )

