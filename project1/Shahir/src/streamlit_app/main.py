import streamlit as st
from src.streamlit_app.pages.dashboard import show_hospital_dashboard
from src.streamlit_app.pages.batch_process import show_batch_process
from src.streamlit_app.pages.query_editor import show_query_editor
from src.streamlit_app.pages.upload import show_data_migration
import pandas as pd 
st.set_page_config(
    page_title='Ampera',
    layout='wide'
)
if 'rerun_required' not in st.session_state:
    st.session_state.rerun_required=False
st.title('Ampera')
dashboard_tab,upload_tab,query_tab,batch_tab=st.tabs([
    'Dashboard',
    'Upload',
    'Query tool',
    'Batch Process'
])

with dashboard_tab:
    try:
        show_hospital_dashboard()
    except:
        st.write('There is nothing to show!')


# Tab 2
with upload_tab:
    
    show_data_migration()
   

# Tab 3
with query_tab:
    try:
        show_query_editor()
    except:
        st.write('There is nothing to show in query tab!')

# Tab 4
with batch_tab:

    show_batch_process()
   
