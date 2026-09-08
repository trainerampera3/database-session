import streamlit as st
import pandas as pd

from components.db_connection import get_connection


conn = get_connection()

st.set_page_config(
    page_title="Data Migration Tool",
    layout="wide"
)

df = None
with conn.cursor() as cur:
    

    with st.form("my_form"):
        
        query = st.text_area(label='Enter your Query', value='Select * from airport')
        
        
        submitted = st.form_submit_button("Submit")
        
           
                

        if submitted:
            if query.lower().startswith("select"):
            
                try:
                    cur.execute(query)
                    row = cur.fetchmany(50)
                    df = pd.DataFrame(
                        row,
                        columns=[desc.name for desc in cur.description]
                    )
                    st.dataframe(df)
                    
                    
                except Exception as e:
                    st.error(f'Some Error Occured {e}')
            else:
                st.error('Only select statements are allowed')

    if df is not None:
        csv = df.to_csv(index=False)
        
        st.download_button(
            "Download CSV",
            data=csv,
            file_name="output.csv",
            mime="text/csv"
        )
        

