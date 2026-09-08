import pandas as pd
import streamlit as st
from components.logger import logger
from components.db_connection import get_connection


conn = get_connection()

def upload_csv():
    st.write("Upload CSV")
    
    uploaded_file = st.file_uploader(
        "Upload your CSV file",
        type=["csv"]
    )

    if uploaded_file:
        st.session_state.id += 1
        st.session_state.file_name = uploaded_file.name
        logger.info(f"{uploaded_file.name} file was uploaded")

        df = pd.read_csv(uploaded_file)

        st.session_state.df = df

        st.success(
            f"{len(df):,} rows loaded successfully"
        )
        

        st.dataframe(df.head())
        with conn.cursor() as cur:
            cur.execute("""Insert into batchlog(batch_id, source_file,stage, updated_at, batch_no) values (%s, %s,%s,NOW() AT TIME ZONE 'Asia/Kolkata', %s);""",(f"BAT-{st.session_state.id}", uploaded_file.name, 'upload',st.session_state.id))
        conn.commit()


def analyse():
    st.header("Analyse Data")
    
    df = st.session_state.df
    
    col1, col2, col3= st.columns(3)
    
    with col1:
    
        st.metric(
        'Rows Parsed',
        len(df)
        )
    with col2:
        st.metric(
            'Columns',
            len(df.columns)
        )
    
    with col3:
        completeness = (1 - df.isnull().sum().sum() / df.size) * 100
        uniqueness = (1 - df.duplicated().sum() / len(df)) * 100
        score = (completeness + uniqueness) / 2
        st.metric('Quality Score',f'{round(score, 2)}/100')

    
    profile = pd.DataFrame({
        "Column": df.columns,
        "Type": df.dtypes.astype(str),
        "Null %": (
            df.isnull().mean() * 100
        ).round(2),
        "Distinct": df.nunique(),
        'Sample':df.loc[10]
    })
    logger.info(f'{st.session_state.file_name} is analysed')
    with conn.cursor() as cur:
        cur.execute("""update batchlog set stage = %s, updated_at = NOW() AT TIME ZONE 'Asia/Kolkata' where batch_id = %s;""",('analyse',f"BAT-{st.session_state.id}"))
    conn.commit()

    
    st.dataframe(
        profile,
        use_container_width=True
    )
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
    
        if st.button(
            "← Back",
            key="analysis_back"
        ):
    
            st.session_state.step = 0
            st.rerun()
        if st.button("Reset"):
                st.session_state.step = 0
                st.switch_page("pages/upload.py")

    with col2:
    
        if st.button(
            "Next →",
            key="analysis_next"
        ):
    
            st.session_state.step = 2
            st.rerun()
        




def clean():
    st.header("Clean Data")
    
    df = st.session_state.df

    remove_null = st.checkbox(
        'Remove null Values', value=True
    )

    remove_duplicates = st.checkbox(
        "Remove duplicate rows",
        value=True
    )

    trim_strings = st.checkbox(
        "Trim spaces",
        value=True
    )

    convert_dates = st.checkbox(
        "Convert date columns",
        value=True
    )

    if st.button(
        "Apply Cleaning",
        key="apply_cleaning"
    ):

        

        if remove_null :

            df = df.dropna()

        if remove_duplicates:

            df = df.drop_duplicates()

        if trim_strings:

            object_cols = df.select_dtypes(
                include=["object"]
            ).columns

            for col in object_cols:

                df[col] = (
                    df[col]
                    .astype(str)
                    .str.strip()
                )

        if convert_dates:

            for col in df.columns:

                if "date" in col.lower():

                    df[col] = pd.to_datetime(
                        df[col],
                        errors="coerce"
                    )
        st.session_state.df = df
        logger.info(f'{st.session_state.file_name} is cleaned')
        with conn.cursor() as cur:
            cur.execute("""update batchlog set stage = %s, updated_at =NOW() AT TIME ZONE 'Asia/Kolkata' where batch_id = %s;""",('clean',f"BAT-{st.session_state.id}"))
        conn.commit()
        

        st.success(
            "Cleaning completed!"
        )

        st.write(
            f"Rows after cleaning: "
            f"{len(df):,}"
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "← Back",
            key="clean_back"
        ):

            st.session_state.step = 1
            st.rerun()
        if st.button("Reset"):
            st.session_state.step = 0
            st.switch_page("pages/upload.py")

    with col2:

        if st.button(
            "Next →",
            key="clean_next"
        ):

            st.session_state.step = 3
            st.rerun()
    


def col_map():
    st.header("Column Mapping")
    
    df = st.session_state.df
    
    
    columns = df.columns
    options = st.multiselect(
        "What are your favorite cat names?",
        columns,
        accept_new_options=True,
    )
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("You selected:", options)
    with col2:
        st.write(df.loc[10])
    
    
    t_name = st.text_input('your table name', placeholder='table Name').lower().strip()
    st.session_state.tname = t_name
    st.write(st.session_state.tname)
    
    mapping = {}
    const = []
    
    for column in options:
        mapping[column] = st.text_input(
            f"Map `{column}`",
            placeholder="Column name in database"
        ).strip()
    st.divider()
    
    if all(mapping.values()):
        const = []
        for column in mapping.values():
            val = st.text_input(f"Datatype for `{column}`", placeholder='Datatype with constraints', key=f"input {column}").strip()
            const.append(column + " " + val)
    
    else:
        st.info('Fill all column mappings first')
    
    
    
    st.write(mapping)
    
    st.session_state.mapping = mapping
    st.session_state.const = const
    st.write(st.session_state.const)
    st.write(st.session_state.mapping)
    
    st.divider()
    logger.info(f'{st.session_state.file_name} is mapped to databse table {t_name}')
    with conn.cursor() as cur:
        cur.execute("""update batchlog set stage = %s , updated_at = NOW() AT TIME ZONE 'Asia/Kolkata' where batch_id = %s;""",('Map',f"BAT-{st.session_state.id}"))
    conn.commit()
    
    
    col1, col2 = st.columns(2)
    
    with col1:
    
        if st.button(
            "← Back",
            key="mapping_back"
        ):
    
            st.session_state.step = 2
            st.rerun()
        if st.button("Reset"):
            st.session_state.step = 0
            st.switch_page("pages/upload.py")
    
    with col2:
    
        if st.button(
            "Next →",
            key="mapping_next"
        ):
    
            st.session_state.step = 4
            st.rerun()