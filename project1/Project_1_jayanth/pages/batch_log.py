import streamlit as st
import pandas as pd

from components.db_connection import get_connection



st.header('Batch Process Log')
st.markdown('Every CSV ingest run — upload, analyse, clean, map, migrate')

col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric('batches', 18)

with col2:
    st.metric('Rows Ingested', st.session_state.success)

with col3:
    st.metric('Rows Rejected',st.session_state.failed)

conn = get_connection()

try:
    df = pd.read_sql_query('select * from batchlog order by updated_at DESC ', conn)
    df['updated_at'] = (
    pd.to_datetime(df['updated_at'], utc=True)
      .dt.tz_convert('Asia/Kolkata')
    )
    

    st.dataframe(df)
except:
    st.write('Something wrong')


