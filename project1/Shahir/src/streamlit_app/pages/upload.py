import streamlit as st
import pandas as pd
import logging
import time
from utils.db_helper import load_data_using_insertions,insert_db,update_db
from utils.database_connection import connection
from transformations.transform import filter
from pathlib import Path

logging.basicConfig(level=logging.INFO)


def show_upload_tab():

    st.header("Upload")

    uploaded_file = st.file_uploader(
        "Upload your CSV file",
        type=["csv"]
    )

    if uploaded_file:
        upload_folder='data/raw'
        file_path = Path(upload_folder) / uploaded_file.name
        st.session_state.file_path = file_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        logging.info(f"File saved to {file_path}")

        st.session_state.df = pd.read_csv(uploaded_file)

        st.success("File uploaded successfully!")
        if st.session_state.file_name is None:
            st.session_state.file_name = uploaded_file.name


        if st.button("Save", key="upload"):

            insert_db(
                str(uploaded_file.name),
                "Upload",
                len(st.session_state.df),
                "Running",
                str(file_path)
            )

    else:
        st.session_state.df = None


def show_analyze_tab():

    st.header("Analyze")

    dataframe = st.session_state.df

    if dataframe is not None and not dataframe.empty:

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Count",
                len(dataframe)
            )

        with col2:
            st.metric(
                "Cols Count",
                dataframe.shape[1]
            )

        with col3:

            completeness = (
                1 - dataframe.isnull().mean().mean()
            )

            uniqueness = (
                dataframe.drop_duplicates().shape[0]
                / len(dataframe)
            )

            quality_score = (
                completeness * 0.5
                + uniqueness * 0.5
            ) * 100

            st.metric(
                "Quality Score",
                round(quality_score, 2)
            )

        with col4:
            st.metric(
                "Issues Found",
                2
            )

        column_info = pd.DataFrame({
            "Column": dataframe.columns,

            "Data Type":
                dataframe.dtypes.astype(str).values,

            "Distinct Count":
                dataframe.nunique().values,

            "First Non-Null":
                dataframe.apply(
                    lambda col:
                    col.dropna().iloc[0]
                    if not col.dropna().empty
                    else None
                ).values,

            "Null %":
                (
                    dataframe.isnull().mean() * 100
                ).map(
                    lambda x: f"{x:.2f}%"
                )
        })

        column_info["First Non-Null"] = (
            column_info["First Non-Null"].astype(str)
        )

        st.dataframe(
            column_info,
            use_container_width=True
        )

        if st.button("Save", key="running"):

            update_db(
                str(st.session_state.file_name),
                "Analyse",
                len(dataframe),
                "Running",
                str(st.session_state.file_path)
            )

    else:
        st.write("No Data Found!")


def show_clean_tab():

    st.header("Clean")

    if (
        st.session_state.df is None
        or st.session_state.df.empty
    ):
        st.warning("Please upload a file first.")
        return

    null_values = st.checkbox(
        "Remove null values!"
    )

    duplicate_values = st.checkbox(
        "Remove Duplicates!"
    )

    data_type_change = st.checkbox(
        "Convert the Dates into Date datatype"
    )

    format_data = st.checkbox(
        "Format the Gender correctly"
    )

    to_lowercase = st.checkbox(
        "Change all string columns to lowercase"
    )

    to_uppercase = st.checkbox(
        "Change all string columns to uppercase"
    )

    st.session_state.c_df = filter(
        st.session_state.df,
        null_values,
        duplicate_values,
        data_type_change,
        format_data,
        to_lowercase,
        to_uppercase
    )

    st.write("Preview")

    st.dataframe(
        st.session_state.c_df,
        use_container_width=True
    )

    if st.button("Save", key="cleaning"):
        upload_folder='data/cleaned'
        file_path= Path(upload_folder) / f'cleaned_{st.session_state.file_name}'
        st.session_state.cleaned_file_path = file_path
        st.session_state.c_df.to_csv(file_path, index=False)
        update_db(
                    str(st.session_state.file_name),
                    "Clean",
                    len(st.session_state.c_df),
                    "Running",
                    str(st.session_state.cleaned_file_path)
                )
        
        logging.info(f"Cleaned file saved to {file_path}")

        

def show_map_tab():

    st.header("Map Columns")

    if (
        st.session_state.c_df is None
        or st.session_state.c_df.empty
    ):
        st.warning("Please clean the data first.")
        return

    conn = connection()

    with conn.cursor() as cursor:

        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'patients'
            ORDER BY ordinal_position;
        """)

        cols = []
        dtypes = []

        for row in cursor.fetchall():
            cols.append(row[0])
            dtypes.append(row[1])

    type_mapping = {

        "int64": [
            "integer",
            "bigint"
        ],

        "int32": [
            "integer"
        ],

        "float64": [
            "double precision",
            "real",
            "numeric"
        ],

        "float32": [
            "real",
            "double precision",
            "numeric"
        ],

        "object": [
            "character varying",
            "text"
        ],

        "string": [
            "character varying",
            "text"
        ],

        "bool": [
            "boolean"
        ],

        "datetime64[us]": [
            "timestamp without time zone",
            "timestamp with time zone",
            "date"
        ]
    }

    dataframe = st.session_state.c_df

    results = []

    for p_col, p_dtype, d_col, d_dtype in zip(
        dataframe.columns,
        dataframe.dtypes,
        cols,
        dtypes
    ):

        pandas_type = str(p_dtype)

        if d_dtype in type_mapping.get(
            pandas_type,
            []
        ):
            result = "Done"
        else:
            result = "Not Matched!"

        results.append(result)

    frame = pd.DataFrame({

        "Source Columns":
            dataframe.columns,

        "Target Columns":
            cols,

        "Target Data Type":
            dtypes,

        "DataFrame Dtype":
            dataframe.dtypes.astype(str).values,

        "Matched":
            results
    })

    st.dataframe(
        frame,
        use_container_width=True
    )

    if st.button("Save", key="run"):

        update_db(
            str( st.session_state.file_name),
            "Map",
            len(dataframe),
            "Running",
            str(st.session_state.cleaned_file_path)
        )


def show_migrate_tab():

    st.header("Migrate")

    st.write(
        "Migrate your cleaned and mapped data here."
    )

    if (
        st.session_state.c_df is None
        or st.session_state.c_df.empty
    ):
        st.warning(
            "Please clean the data before migrating."
        )
        return

    if st.button("Migrate", key="migrate"):

        start_time = time.time()

        update_db(
            str(st.session_state.file_name),
            "Migrating",
            len(st.session_state.c_df),
            "Running",
            str(st.session_state.cleaned_file_path)
        )

        progress_bar = st.progress(0, text="Migrating data to database...")

        def update_progress(value):
            progress_bar.progress(value, text=f"Migrating data to database... {int(value * 100)}%")

        processed_rows = load_data_using_insertions(
            st.session_state.c_df,
            st.session_state.file_name,
            progress_callback=update_progress
        )

        progress_bar.empty()

        end_time = time.time()

        duration = end_time - start_time

        update_db(
            str(st.session_state.file_name),
            "Migrate",
            len(st.session_state.c_df),
            "Done",
            str(st.session_state.cleaned_file_path),
            duration,
            processed_rows

        )

        st.success("Migration completed successfully!")
    

def show_data_migration():

    st.title("Data Migration Tool")

    # Session state
    if "df" not in st.session_state:
        st.session_state.df = None

    if "c_df" not in st.session_state:
        st.session_state.c_df = None

    if "file_path" not in st.session_state:
        st.session_state.file_path = None
    if 'file_name' not in st.session_state:
        st.session_state.file_name = None
    if 'cleaned_file_path' not in st.session_state:
        st.session_state.cleaned_file_path = None

    # Tabs
    (
        upload_tab,
        analyze_tab,
        clean_tab,
        map_tab,
        migrate_tab
    ) = st.tabs([
        "Upload",
        "Analyze",
        "Clean",
        "Map Columns",
        "Migrate"
    ])

    with upload_tab:
        show_upload_tab()

    with analyze_tab:
        show_analyze_tab()

    with clean_tab:
        show_clean_tab()

    with map_tab:
        show_map_tab()

    with migrate_tab:
        show_migrate_tab()
    if st.session_state.df is not None:
        return len(st.session_state.c_df)
    else:
        return -1