import streamlit as st



from components.up_helper import upload_csv, analyse, clean, col_map
from components.migration import migration
from components.db_connection import get_connection


conn = get_connection()



st.subheader('Load CSV file into Database')

st.markdown('Upload, profile, clean and map your file — then migrate it and read it on your dashboards.')

st.divider()


with conn.cursor() as cur:
    cur.execute('select max(batch_no) from batchlog;')
    maxn = cur.fetchone()
    print(maxn[0])
    st.session_state.id = maxn[0]



if "step" not in st.session_state:
    st.session_state.step = 0

if "df" not in st.session_state:
    st.session_state.df = None


if st.session_state.id == None:
    st.session_state.id = 0
    print(st.session_state.id)



steps = [
    "Upload",
    "Analyse",
    "Clean",
    "Mapping",
    "Migration"
]
cols = st.columns(len(steps))

for i, step_name in enumerate(steps):

    with cols[i]:

        if i == st.session_state.step:
            st.markdown(
                f" 🟢 {step_name}"
            )
        elif i < st.session_state.step:
            st.markdown(
                f" ✅ {step_name}"
            )
        else:
            st.markdown(
                f" ⚪ {step_name}"
            )




st.divider()



if st.session_state.step == 0:

   

    upload_csv()



    st.divider()

    if st.button(
        "Next →",
        key="upload_next"
    ):

        if st.session_state.df is None:

            st.warning(
                "Please upload a CSV first."
            )

        else:

            st.session_state.step = 1
            st.rerun()
    if st.button("Reset"):
            st.session_state.step = 0
            st.switch_page("pages/upload.py")

elif st.session_state.step == 1:
    analyse()


    
elif st.session_state.step == 2:
    clean()


    
elif st.session_state.step == 3:
    col_map()



    
elif st.session_state.step == 4:
    migration(conn)
    st.divider()

    if st.button("← Back",key="migration_back"):
        st.session_state.step = 3
        st.rerun()
    if st.button("Go to Dashboard"):
        st.session_state.step = 0
        st.switch_page("pages/dashboard.py")
