import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg
from processing.cleaning import (
    clean_spaces,
    clean_duplicates,
    clean_capitalization,
    clean_remote_work,
    clean_numeric_columns,
    clean_experience,
    clean_salary,
    clean_salary_range,
    clean_ai_salary_premium,
    clean_posting_month,
    clean_boolean_columns,
    remove_null_rows,
)
from processing.transform import transform_dataset
from processing.validate import validate_dataset
from pipelines.run_pipeline import process_batches

def get_db_connection():

    return psycopg.connect(
        host="localhost",
        port=5433,
        dbname="job_management",
        user="deepika",
        password="deepu1014"
    )


@st.cache_data
def load_database_data():
    conn = None
    try:
        conn = get_db_connection()
        query = """
            SELECT
                j.job_id,
                j.job_title,
                j.job_category,
                j.experience_level,
                j.years_of_experience,
                j.education_required,
                j.city,
                j.country,
                j.remote_work,
                j.company_size,
                j.industry,
                j.required_skills,

                jm.is_senior,
                jm.is_remote_friendly,
                jm.is_llm_role,
                jm.annual_salary_usd,
                jm.salary_min_usd,
                jm.salary_max_usd,
                jm.ai_salary_premium_pct,
                jm.demand_score,
                jm.demand_growth_yoy_pct,
                jm.benefits_score_10,
                jm.posting_year,
                jm.posting_month

            FROM jobs j

            LEFT JOIN jobs_market jm
                ON j.job_id = jm.job_id
        """

        df = pd.read_sql_query(
            query,
            conn
        )
        return df

    finally:

        if conn is not None:
            conn.close()



def load_batch_logs_from_db():
    conn = None
    try:
        conn = get_db_connection()
        query = """
            SELECT
                run_id,
                pipeline_started,
                completed,
                status,
                records,
                error
            FROM batch_log
            ORDER BY pipeline_started DESC
        """
        
        df = pd.read_sql_query(
            query,
            conn
        )
        
        return df
    
    except Exception as e:
        
        st.error(
            f"Could not load batch logs from database: {e}"
        )
        
        return pd.DataFrame()
    
    finally:
       
        if conn is not None:
            conn.close()


st.set_page_config(
    page_title="Job Management Dashboard",
    layout="wide"
)


if "transformed_df" not in st.session_state:
    st.session_state.transformed_df = None

if "validated_df" not in st.session_state:
    st.session_state.validated_df = None


st.title("Job Management Dashboard")



if "datasets" not in st.session_state:
    st.session_state["datasets"] = {}

if "cleaned_datasets" not in st.session_state:
    st.session_state["cleaned_datasets"] = {}

if "column_mappings" not in st.session_state:
    st.session_state["column_mappings"] = {}

if "batch_logs" not in st.session_state:
    st.session_state["batch_logs"] = []

if "migration_summary" not in st.session_state:
    st.session_state["migration_summary"] = {
        "records_processed": 0,
        "successful_batches": 0,
        "failed_batches": 0,
        "last_run": None,
    }


tab1, tab2, tab3, tab4 = st.tabs([
    "Upload Data",
    "Query Editor",
    "Batch Log",
    "Dashboard"
])



with tab1:
    st.header("Upload Data")

    

    upload_tab1, upload_tab2, upload_tab3, upload_tab4, upload_tab5 = st.tabs([
        "Upload CSV",
        "Analyse",
        "Clean",
        "Map Columns",
        "Migrate"
    ])
    # 1. UPLOAD CSV
    with upload_tab1:
        st.subheader("Upload CSV Files")
        uploaded_files = st.file_uploader(
            "Choose one or more CSV files",
            type=["csv"],
            accept_multiple_files=True,
            key="csv_uploader"
        )


        current_file_names = set()

        if uploaded_files:
            current_file_names = {
                file.name
                for file in uploaded_files
            }
        

        existing_file_names = set(
            st.session_state["datasets"].keys()
        )
        removed_files = (
            existing_file_names - current_file_names
        )
        for file_name in removed_files:

            del st.session_state["datasets"][file_name]

            if file_name in st.session_state["cleaned_datasets"]:
                del st.session_state["cleaned_datasets"][file_name]

            if file_name in st.session_state["column_mappings"]:
                del st.session_state["column_mappings"][file_name]


        new_files = []

        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_name = uploaded_file.name
                if file_name not in st.session_state["datasets"]:
                    try:
                        # Read CSV in batches
                        batch_size = 100
                        batches = []

                        for batch in pd.read_csv(
                            uploaded_file,
                            chunksize=batch_size
                        ):

                            batches.append(batch)

                        
                        df = pd.concat(
                            batches,
                            ignore_index=True
                        )

                        st.session_state[
                            "datasets"
                        ][file_name] = df

                        new_files.append(
                            file_name
                        )

                    except Exception as e:

                        st.error(
                            f"Could not read {file_name}: {e}"
                        )
        
        if new_files:
            if len(new_files) == 1:
                st.success(
                    f"File uploaded successfully: "
                    f"{new_files[0]}"
                )
            else:
                st.success(
                    f"{len(new_files)} files uploaded successfully!"
                )

        

        if st.session_state["datasets"]:
            st.subheader(
                "Uploaded Datasets"
            )
            for file_name, df in st.session_state[
                "datasets"
            ].items():

                with st.expander(
                    f"{file_name}",
                    expanded=False
                ):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "Rows",
                            df.shape[0]
                        )
                    with col2:
                        st.metric(
                            "Columns",
                            df.shape[1]
                        )
                    with col3:
                        st.metric(
                            "Duplicates",
                            int(
                                df.duplicated().sum()
                            )
                        )
                    st.dataframe(
                        df.head(10),
                        use_container_width=True
                    )

        else:
            st.info(
                "No datasets uploaded yet."
            )

    # 2. ANALYSE 

    with upload_tab2:
        st.subheader(
            "Analyse Dataset"
        )
        if not st.session_state["datasets"]:
            st.warning(
                "Please upload at least one CSV file first."
            )
        else:
            dataset_names = list(
                st.session_state[
                    "datasets"
                ].keys()
            )
            selected_dataset = st.selectbox(
                "Select Dataset to Analyse",
                dataset_names,
                key="analyse_dataset"
            )

            df = st.session_state[
                "datasets"
            ][selected_dataset].copy()

            st.write(
                f"### Dataset: `{selected_dataset}`"
            )

            

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "Total Rows",
                    df.shape[0]
                )
            with col2:
                st.metric(
                    "Total Columns",
                    df.shape[1]
                )
            with col3:
                st.metric(
                    "Duplicate Rows",
                    int(
                        df.duplicated().sum()
                    )
                )
            with col4:
                st.metric(
                    "Missing Values",
                    int(
                        df.isna()
                        .sum()
                        .sum()
                    )
                )
            st.divider()

            

            st.subheader(
                "Column Information"
            )
            analysis_data = []

            for column in df.columns:

                analysis_data.append({
                    "Column": column,
                    "Data Type": str(
                        df[column].dtype
                    ),
                    "Missing Values": int(
                        df[column].isna().sum()
                    ),
                    "Missing %": round(
                        df[column]
                        .isna()
                        .mean()
                        * 100,
                        2
                    ),
                    "Unique Values": int(
                        df[column]
                        .nunique(
                            dropna=True
                        )
                    )
                })

            analysis_df = pd.DataFrame(
                analysis_data
            )

            st.dataframe(
                analysis_df,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            

            st.subheader(
                "Duplicate Analysis"
            )

            duplicate_count = int(
                df.duplicated().sum()
            )

            if duplicate_count == 0:

                st.success(
                    "No duplicate rows found."
                )

            else:

                st.warning(
                    f"{duplicate_count} duplicate rows found."
                )

                duplicate_rows = df[
                    df.duplicated(
                        keep=False
                    )
                ]

                with st.expander(
                    "View Duplicate Rows"
                ):

                    st.dataframe(
                        duplicate_rows,
                        use_container_width=True
                    )

            st.divider()

            

            st.subheader(
                "Missing Value Analysis"
            )

            missing_data = []

            for column in df.columns:

                missing_count = int(
                    df[column]
                    .isna()
                    .sum()
                )

                if missing_count > 0:

                    missing_data.append({
                        "Column": column,
                        "Missing Values": missing_count,
                        "Missing %": round(
                            (
                                missing_count
                                / len(df)
                                * 100
                            ),
                            2
                        )
                    })

            if missing_data:

                missing_df = pd.DataFrame(
                    missing_data
                )

                st.dataframe(
                    missing_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.success(
                    "No missing values found."
                )

            st.divider()

            

            st.subheader(
                "Data Preview"
            )

            st.dataframe(
                df.head(20),
                use_container_width=True
            )

    # 3. CLEAN

    with upload_tab3:

        st.header(
            "Clean Dataset"
        )
        if not st.session_state["datasets"]:

            st.warning(
                "Please upload a CSV file first."
            )
        else:
            dataset_names = list(
                st.session_state[
                    "datasets"
                ].keys()
            )

            selected_dataset = st.selectbox(
                "Select Dataset to Clean",
                dataset_names,
                key="selected_clean_dataset"
            )

            df = st.session_state[
                "datasets"
            ][selected_dataset].copy()

            st.write(
                f"**Selected Dataset:** "
                f"{selected_dataset}"
            )

            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Rows",
                    len(df)
                )
            with col2:
                st.metric(
                    "Columns",
                    len(df.columns)
                )
            with col3:
                st.metric(
                    "Duplicates",
                    int(
                        df.duplicated().sum()
                    )
                )

            st.divider()

            

            st.subheader(
                "Cleaning Options"
            )

            
            fix_duplicates = st.checkbox(
                "Remove Duplicate Rows",
                value=True,
                key="fix_duplicates"
            )
            
            fix_spaces = st.checkbox(
                "Remove Leading and Trailing Spaces",
                value=True,
                key="fix_spaces"
            )
            
            fix_capitalization = st.checkbox(
                "Fix Inconsistent Capitalization",
                value=True,
                key="fix_capitalization"
            )
            st.caption(
                "Standardizes values such as "
                "entry / Entry / ENTRY."
            )
            
            fix_experience = st.checkbox(
                "Fix Experience Level",
                value=True,
                key="fix_experience"
            )
            st.caption(
                "0–3 = Entry | "
                "4–8 = Mid | "
                "9–12 = Senior | "
                "13+ = Lead"
            )
            
            fix_salary = st.checkbox(
                "Fix Annual Salary according to Experience Level",
                value=True,
                key="fix_salary"
            )
            st.caption(
                "Entry: $30,000–$50,000 | "
                "Mid: $50,000–$70,000 | "
                "Senior: $70,000–$100,000 | "
                "Lead: above $100,000"
            )
            
            fix_salary_range = st.checkbox(
                "Fix Salary Minimum and Maximum",
                value=True,
                key="fix_salary_range"
            )

            

            fix_ai_premium = st.checkbox(
                "Fix AI Salary Premium %",
                value=True,
                key="fix_ai_premium"
            )

            st.caption(
                "AI Salary Premium must be between "
                "0% and 100%."
            )
            
            fix_posting_month = st.checkbox(
                "Fix Posting Month",
                value=True,
                key="fix_posting_month"
            )
            st.caption(
                "Posting Month must be between "
                "1 and 12."
            )
            
            fix_boolean = st.checkbox(
                "Normalize Yes / No Boolean Values",
                value=True,
                key="fix_boolean"
            )
            st.caption(
                "Yes / True / 1 → 1 | "
                "No / False / 0 → 0"
            )
            
            fix_nulls = st.checkbox(
                "Handle Missing / NULL Values",
                value=True,
                key="fix_nulls"
            )
            
            missing_count = int(
                df.isna()
                .sum()
                .sum()
            )

            if missing_count > 0:

                st.caption(
                    f"Current missing values: "
                    f"{missing_count}"
                )
            st.divider()
            

            if st.button(
                "Clean Data",
                type="primary",
                use_container_width=True,
                key="clean_data_button"
            ):
                cleaned_df = df.copy()
                
                if fix_spaces:
                    cleaned_df = clean_spaces(
                        cleaned_df
                    )
                
                if fix_duplicates:
                    cleaned_df = clean_duplicates(
                        cleaned_df
                    )
                
                if fix_capitalization:
                    cleaned_df = clean_capitalization(
                        cleaned_df
                    )
                
                cleaned_df = clean_remote_work(
                    cleaned_df
                )
                
                cleaned_df = clean_numeric_columns(
                    cleaned_df
                )
                
                if fix_experience:
                    cleaned_df = clean_experience(
                        cleaned_df
                    )
                
                if fix_salary:
                    cleaned_df = clean_salary(
                        cleaned_df
                    )
                
                if fix_salary_range:
                    cleaned_df = clean_salary_range(
                        cleaned_df
                    )
                
                if fix_ai_premium:
                    cleaned_df = clean_ai_salary_premium(
                        cleaned_df
                    )
                
                if fix_posting_month:
                    cleaned_df = clean_posting_month(
                        cleaned_df
                    )
                
                if fix_boolean:
                    cleaned_df = clean_boolean_columns(
                        cleaned_df
                    )
                
                if fix_nulls:
                    cleaned_df = remove_null_rows(
                        cleaned_df
                    )
                
                if fix_spaces:
                    cleaned_df = clean_spaces(
                        cleaned_df
                    )
                
                st.session_state[
                    "cleaned_datasets"
                ][selected_dataset] = cleaned_df

                st.success(
                    "Dataset cleaned successfully!"
                )

            # CLEANED DATA PREVIEW

            if (
                selected_dataset
                in st.session_state[
                    "cleaned_datasets"
                ]
            ):

                cleaned_df = st.session_state[
                    "cleaned_datasets"
                ][selected_dataset]

                st.divider()

                st.subheader(
                    "Cleaned Dataset Preview"
                )

                st.dataframe(
                    cleaned_df.head(20),
                    use_container_width=True
                )

                st.divider()

                csv_data = (
                    cleaned_df
                    .to_csv(
                        index=False
                    )
                    .encode("utf-8")
                )

                st.download_button(
                    "⬇ Download Cleaned CSV",
                    data=csv_data,
                    file_name=(
                        "cleaned_"
                        + selected_dataset
                    ),
                    mime="text/csv",
                    use_container_width=True,
                    key="download_cleaned_csv"
                )

    # 4. MAP COLUMNS

    with upload_tab4:

        st.header("Map Columns")

        st.info(
            "Map the cleaned CSV columns to the target PostgreSQL columns."
        )
        

        TARGET_COLUMNS = {
            "jobs": {
                "job_id": ("varchar", "job_id"),
                "job_title": ("varchar", "job_title"),
                "job_category": ("varchar", "job_category"),
                "experience_level": ("varchar", "experience_level"),
                "years_of_experience": ("integer", "years_of_experience"),
                "education_required": ("varchar", "education_required"),
                "city": ("varchar", "city"),
                "country": ("varchar", "country"),
                "remote_work": ("varchar", "remote_work"),
                "company_size": ("varchar", "company_size"),
                "industry": ("varchar", "industry"),
                "required_skills": ("text", "required_skills"),
                "is_senior": ("boolean", "is_senior"),
                "is_remote_friendly": ("boolean", "is_remote_friendly"),
                "is_llm_role": ("boolean", "is_llm_role"),
            },

            "jobs_market": {
                "job_id": ("varchar", "job_id"),
                "annual_salary_usd": ("numeric", "annual_salary_usd"),
                "salary_min_usd": ("numeric", "salary_min_usd"),
                "salary_max_usd": ("numeric", "salary_max_usd"),
                "ai_salary_premium_pct": (
                    "numeric",
                    "ai_salary_premium_pct"
                ),
                "demand_score": ("integer", "demand_score"),
                "demand_growth_yoy_pct": (
                    "numeric",
                    "demand_growth_yoy_pct"
                ),
                "benefits_score_10": (
                    "numeric",
                    "benefits_score_10"
                ),
                "posting_year": ("integer", "posting_year"),
                "posting_month": ("integer", "posting_month"),
            }
        }

        

        if not st.session_state["datasets"]:

            st.warning(
                "Please upload a CSV file first."
            )
        else:
            dataset_names = list(
                st.session_state["datasets"].keys()
            )

            selected_dataset = st.selectbox(
                "Select Dataset",
                dataset_names,
                key="map_dataset"
            )

            

            if selected_dataset not in st.session_state[
                "cleaned_datasets"
            ]:

                st.warning(
                    "Please clean this dataset before mapping columns."
                )
            else:
                df = st.session_state[
                    "cleaned_datasets"
                ][selected_dataset].copy()

                st.subheader("Target Database")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(
                        "**Database:** `job`"
                    )
                with col2:
                    st.write(
                        "**Mode:** `Append`"
                    )

                st.divider()

                
                source_columns = list(
                    df.columns
                )
                
                target_definitions = []
                for table_name, columns in TARGET_COLUMNS.items():

                    for target_column, details in columns.items():
                        target_type, target_name = details
                        target_definitions.append({
                            "table": table_name,
                            "target": target_name,
                            "type": target_type
                        })

                
                def normalize_column_name(name):

                    return (
                        str(name)
                        .strip()
                        .lower()
                        .replace(" ", "_")
                        .replace("-", "_")
                    )
                normalized_sources = {
                    normalize_column_name(column): column
                    for column in source_columns
                }
                

                mapping_rows = []
                used_source_columns = set()

                for target in target_definitions:

                    target_name = target["target"]
                    target_type = target["type"]
                    table_name = target["table"]

                    normalized_target = (
                        normalize_column_name(
                            target_name
                        )
                    )

                    
                    if normalized_target in normalized_sources:

                        source_column = (
                            normalized_sources[
                                normalized_target
                            ]
                        )

                        match_type = "Exact"

                        used_source_columns.add(
                            source_column
                        )

                    else:

                        source_column = None
                        match_type = "Not Found"

                    mapping_rows.append({
                        "Source": source_column,
                        "Target Name": target_name,
                        "Target Type": target_type,
                        "Table": table_name,
                        "Match": match_type
                    })

                

                mapped_sources = {
                    row["Source"]
                    for row in mapping_rows
                    if row["Source"] is not None
                }

                skipped_columns = [
                    column
                    for column in source_columns
                    if column not in mapped_sources
                ]
                
                mapped_count = len(mapped_sources)

                total_source_columns = len(
                    source_columns
                )

                skipped_count = len(
                    skipped_columns
                )

                st.subheader(
                    f"Map to PostgreSQL"
                )

                st.write(
                    f"**{mapped_count} of "
                    f"{total_source_columns} columns mapped · "
                    f"{skipped_count} skipped**"
                )

                

                mapping_df = pd.DataFrame(
                    mapping_rows
                )

                st.dataframe(
                    mapping_df,
                    use_container_width=True,
                    hide_index=True
                )

                
                if skipped_columns:

                    st.subheader(
                        "Skipped Source Columns"
                    )

                    for column in skipped_columns:

                        st.write(
                            f"• `{column}` → — not mapped —"
                        )

                

                if st.button(
                    "Save Mapping",
                    type="primary",
                    use_container_width=True,
                    key="save_column_mapping"
                ):
                    column_mapping = {}
                    for row in mapping_rows:

                        source = row["Source"]
                        target = row["Target Name"]

                        if source is not None:

                            column_mapping[source] = target


                    st.session_state[
                        "column_mappings"
                    ][selected_dataset] = column_mapping


                    st.success(
                        "Column mapping saved successfully."
                    )

                
                if selected_dataset in st.session_state[
                    "column_mappings"
                ]:

                    st.divider()

                    st.subheader(
                        "Saved Mapping"
                    )

                    saved_mapping = st.session_state[
                        "column_mappings"
                    ][selected_dataset]

                    saved_mapping_df = pd.DataFrame(
                        [
                            {
                                "Source Column": source,
                                "Target Column": target
                            }
                            for source, target
                            in saved_mapping.items()
                        ]
                    )

                    st.dataframe(
                        saved_mapping_df,
                        use_container_width=True,
                        hide_index=True
                    )
                

                if selected_dataset in st.session_state["column_mappings"]:
                    st.divider()
                    st.subheader("Transform Data")

                    if st.button(
                        "Transform Data",
                        type="primary",
                        use_container_width=True,
                        key="transform_data"
                    ):

                        saved_mapping = st.session_state[
                            "column_mappings"
                        ][selected_dataset]

                        try:
                            transformed_df = transform_dataset(
                                df,
                                saved_mapping
                            )
                            st.session_state[
                                "transformed_df"
                            ] = transformed_df
                            st.success(
                                "Data transformed successfully."
                            )

                            st.write(
                                f"Transformed records: {len(transformed_df)}"
                            )

                            st.dataframe(
                                transformed_df,
                                use_container_width=True,
                                hide_index=True
                            )
                        except Exception as e:

                            st.error(
                                f"Transformation failed: {e}"
                            )
                
                if st.session_state.get("transformed_df") is not None:

                    st.divider()

                    st.subheader("Validate Data")

                    if st.button(
                        "Validate Data",
                        use_container_width=True,
                        key="validate_data"
                    ):

                        transformed_df = st.session_state[
                            "transformed_df"
                        ]
                        try:
                            validation_result = validate_dataset(
                                transformed_df
                            )
                            if validation_result["valid"]:

                                st.success(
                                    "Validation successful. Data is ready for batch processing."
                                )

                                st.session_state[
                                    "validated_df"
                                ] = transformed_df
                                st.session_state[
                                    "validated_row_count"
                                ] = len(transformed_df)

                                st.write(
                                    f"Rows checked / validated: "
                                    f"{len(transformed_df)}"
                                )
                            else:

                                st.error(
                                    f"Validation failed with "
                                    f"{validation_result['error_count']} errors."
                                )

                                for error in validation_result["errors"]:

                                    st.warning(error)

                                st.session_state[
                                    "validated_df"
                                ] = None

                        except Exception as e:

                            st.error(
                                f"Validation failed: {e}"
                            )

                            st.session_state[
                                "validated_df"
                            ] = None

    # 5. MIGRATE

    with upload_tab5:
        st.subheader(
            "Migrate Data"
        )
        if not st.session_state["datasets"]:

            st.warning(
                "Please upload a CSV file first."
            )
        else:
            dataset_names = list(
                st.session_state[
                    "datasets"
                ].keys()
            )
            selected_dataset = st.selectbox(
                "Select Dataset",
                dataset_names,
                key="migrate_dataset"
            )

            if selected_dataset in st.session_state[
                "cleaned_datasets"
            ]:

                cleaned_df = st.session_state[
                    "cleaned_datasets"
                ][selected_dataset]

                migration_df = st.session_state.get(
                    "validated_df"
                )

                if migration_df is None:
                    migration_df = cleaned_df

                st.success(
                    "✓ Cleaned dataset is available."
                )

                st.write(
                    "Records ready for migration: "
                    f"**{len(migration_df)}**"
                )

                if selected_dataset in st.session_state[
                    "column_mappings"
                ]:

                    mapping = st.session_state[
                        "column_mappings"
                    ][selected_dataset]

                    st.info(
                        f"Mapped columns: {len(mapping)}"
                    )

                else:

                    st.warning(
                        "Please map the columns before migration."
                    )

            else:

                st.warning(
                    "Please clean this dataset before migration."
                )

            st.divider()

            can_migrate = (
                selected_dataset in st.session_state["cleaned_datasets"]
                and selected_dataset in st.session_state["column_mappings"]
            )

            if st.button(
                "Migrate to PostgreSQL",
                disabled=not can_migrate,
                use_container_width=True,
                key="migrate_button"
            ):
                try:
                    mapping = st.session_state[
                        "column_mappings"
                    ][selected_dataset]

                    batch_logs = process_batches(
                        st.session_state["cleaned_datasets"][selected_dataset],
                        mapping,
                        batch_size=250
                    )
                    st.session_state["batch_logs"] = batch_logs

                    successful_batches = sum(
                        1 for log in batch_logs
                        if log["status"] == "SUCCESS"
                    )
                    failed_batches = sum(
                        1 for log in batch_logs
                        if log["status"] == "FAILED"
                    )
                    records_processed = sum(
                        log.get("records", 0)
                        for log in batch_logs
                        if log["status"] == "SUCCESS"
                    )

                    st.session_state["migration_summary"] = {
                        "records_processed": records_processed,
                        "successful_batches": successful_batches,
                        "failed_batches": failed_batches,
                        "last_run": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }

                    st.success(
                        f"Migration finished: "
                        f"{successful_batches} successful, "
                        f"{failed_batches} failed."
                    )

                    if failed_batches:
                        st.warning(
                            "Some records were rejected by validation. "
                            "Review the Batch Log tab for details."
                        )

                except Exception as exc:

                    st.error(
                        f"Migration failed: {exc}"
                    )

                    st.session_state["batch_logs"] = []

# QUERY EDITOR TAB

with tab2:
    st.header("Query Editor")

    query = st.text_area(
        "Enter SQL Query",
        height=200,
        placeholder="""
SELECT *
FROM jobs
LIMIT 10;
""",
        key="sql_query"
    )


    if st.button(
        "Run Query",
        type="primary",
        key="run_query"
    ):
        if not query.strip():

            st.warning(
                "Please enter an SQL query."
            )
        else:
            conn = None
            try:

                conn = get_db_connection()

                result = pd.read_sql_query(
                    query,
                    conn
                )

                st.success(
                    "Query executed successfully."
                )

                st.dataframe(
                    result,
                    use_container_width=True,
                    hide_index=True
                )

            except Exception as e:

                st.error(
                    f"Query failed: {e}"
                )

            finally:

                if conn is not None:

                    conn.close()

# BATCH LOG TAB
with tab3:
    st.header("Batch Log")
       
    db_logs_df = load_batch_logs_from_db()
    
        
    if db_logs_df.empty:
        
        st.info(
            "No batch processing records found in database. "
            "Run a migration first to populate this view."
        )
    
    else:
        
        st.success(
            f"Found {len(db_logs_df)} migration run(s) in database"
        )
        
        st.subheader("Migration Runs Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            successful = (db_logs_df["status"] == "SUCCESS").sum()
            st.metric(
                "Successful Runs",
                int(successful)
            )
        
        with col2:
            failed = (db_logs_df["status"] == "FAILED").sum()
            st.metric(
                "Failed Runs",
                int(failed)
            )
        
        with col3:
            total_records = db_logs_df["records"].sum()
            st.metric(
                "Total Records Processed",
                int(total_records)
            )
        
        st.divider()
        
        st.subheader("All Migration Runs")
        st.dataframe(
            db_logs_df,
            use_container_width=True,
            hide_index=True
        )

# DASHBOARD TAB
with tab4:
    st.header("Job Management Dashboard")

    
    try:
        db_df = load_database_data()

    except Exception as e:
        st.error(
            f"Could not load data from PostgreSQL: {e}"
        )

        db_df = pd.DataFrame()

    
    if db_df.empty:

        st.warning(
            "No data found in the PostgreSQL database."
        )

    else:

        st.success(
            f"Data loaded from PostgreSQL successfully — "
            f"{len(db_df)} records."
        )

        
        st.sidebar.header("Filters")
        def unique_values(series):
            if series is None or series.empty:
                return []
            values = (
                series
                .dropna()
                .astype(str)
                .str.strip()
                .loc[lambda s: s != ""]
                .loc[lambda s: ~s.str.lower().isin(["unknown", "n/a", "none", "not specified", "na"]) ]
                .unique()
                .tolist()
            )
            return sorted(values)



        valid_experience_levels = ["Entry", "Mid", "Senior", "Lead"]

        experience_values = unique_values(db_df.get("experience_level"))
        experience_options = [
            value for value in valid_experience_levels
            if value in experience_values
        ]

        selected_experience = st.sidebar.multiselect(
            "Experience Level",
            experience_options,
            default=experience_options,
            key="dashboard_experience_filter",
        )

        category_options = unique_values(db_df.get("job_category"))
        selected_category = st.sidebar.multiselect(
            "Job Category",
            category_options,
            default=category_options,
            key="dashboard_category_filter",
        )

        valid_remote_values = [
            "Fully Remote",
            "Hybrid",
            "On-site",
        ]
        remote_values = unique_values(db_df.get("remote_work"))
        normalized_remote_values = {
            str(value).strip().lower().replace("-", " "): str(value).strip()
            for value in remote_values
            if str(value).strip()
        }
        remote_options = [
            label
            for label in valid_remote_values
            if label.lower().replace("-", " ") in normalized_remote_values
        ]
        selected_remote = st.sidebar.multiselect(
            "Remote Work",
            remote_options,
            default=remote_options,
            key="dashboard_remote_filter",
        )

        job_title_options = unique_values(db_df.get("job_title"))
        selected_job_title = st.sidebar.multiselect(
            "Job Title",
            job_title_options,
            default=job_title_options,
            key="dashboard_job_title_filter",
        )
        # APPLY FILTERS
        filtered_df = db_df.copy()
        if selected_experience:
            filtered_df = filtered_df[
                filtered_df["experience_level"].astype(str).isin(selected_experience)
            ]

        if selected_category:
            filtered_df = filtered_df[
                filtered_df["job_category"].astype(str).isin(selected_category)
            ]

        if selected_remote:
            filtered_df = filtered_df[
                filtered_df["remote_work"].astype(str).isin(selected_remote)
            ]

        if selected_job_title:
            filtered_df = filtered_df[
                filtered_df["job_title"].astype(str).isin(selected_job_title)
            ]

        if filtered_df.empty:
            st.warning("No jobs match the selected filters. Try choosing broader values or clearing some selections.")
            st.stop()

        
        st.subheader("Job Market Overview")

        col1, col2, col3, col4 = st.columns(4)
        with col1:

            total_jobs = filtered_df[
                "job_id"
            ].nunique()

            st.metric(
                "Total Jobs",
                total_jobs
            )

        with col2:

            total_roles = filtered_df[
                "job_title"
            ].nunique()

            st.metric(
                "Job Roles",
                total_roles
            )

        with col3:

            total_categories = filtered_df[
                "job_category"
            ].nunique()

            st.metric(
                "Job Categories",
                total_categories
            )

        with col4:

            avg_experience = filtered_df[
                "years_of_experience"
            ].mean()

            if pd.isna(avg_experience):

                avg_experience = 0

            st.metric(
                "Avg. Experience",
                f"{avg_experience:.1f} years"
            )

        st.divider()

        
        st.subheader("Jobs by Category")
        category_counts = (
            filtered_df["job_category"]
            .value_counts()
            .reset_index()
        )
        category_counts.columns = ["job_category", "job_count"]

        fig = px.bar(
            category_counts,
            x="job_category",
            y="job_count",
            text="job_count"
        )

        fig.update_traces(textposition="outside")

        fig.update_layout(
            xaxis_title="Job Category",
            yaxis_title="Number of Jobs"
        )

        st.plotly_chart(fig, use_container_width=True)

        
        st.subheader("Jobs by Experience Level")
        experience_counts = (
            filtered_df["experience_level"]
            .value_counts()
            .reset_index()
        )
        experience_counts.columns = ["experience_level", "job_count"]

        fig = px.bar(
            experience_counts,
            x="experience_level",
            y="job_count",
            text="job_count"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            xaxis_title="Experience Level",
            yaxis_title="Number of Jobs"
        )
        st.plotly_chart(fig, use_container_width=True)

        
        st.subheader("Remote Work Distribution")
        remote_counts = (
            filtered_df["remote_work"]
            .value_counts()
            .reset_index()
        )
        remote_counts.columns = ["remote_work", "job_count"]

        fig = px.bar(
            remote_counts,
            x="remote_work",
            y="job_count",
            text="job_count"
        )

        fig.update_traces(textposition="outside")

        fig.update_layout(
            xaxis_title="Remote Work",
            yaxis_title="Number of Jobs"
        )

        st.plotly_chart(fig, use_container_width=True)

        
        st.subheader("Top Job Roles")
        top_roles = (
            filtered_df["job_title"]
            .value_counts()
            .head(10)
            .reset_index()
        )
        top_roles.columns = ["job_title", "job_count"]
        fig = px.bar(
            top_roles,
            x="job_title",
            y="job_count",
            text="job_count"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            xaxis_title="Job Role",
            yaxis_title="Number of Jobs"
        )

        st.plotly_chart(fig, use_container_width=True)

        

        st.subheader("Average Salary by Experience Level")
        salary_by_experience = (
            filtered_df
            .groupby("experience_level")["annual_salary_usd"]
            .mean()
            .fillna(0)
            .sort_values(ascending=False)
            .reset_index()
        )
        salary_by_experience.columns = [
            "experience_level",
            "average_salary"
        ]
        fig = px.bar(
            salary_by_experience,
            x="experience_level",
            y="average_salary",
            text="average_salary"
        )
        fig.update_traces(
            texttemplate="$%{text:,.0f}",
            textposition="outside"
        )
        fig.update_layout(
            xaxis_title="Experience Level",
            yaxis_title="Average Salary (USD)"
        )
        st.plotly_chart(fig, use_container_width=True)

        
        st.subheader("Average Demand Score")
        demand_by_category = (
            filtered_df
            .groupby("job_category")["demand_score"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )

        demand_by_category.columns = [
            "job_category",
            "average_demand_score"
        ]

        fig = px.bar(
            demand_by_category,
            x="job_category",
            y="average_demand_score",
            text="average_demand_score"
        )

        fig.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Job Category",
            yaxis_title="Average Demand Score"
        )

        st.plotly_chart(fig, use_container_width=True)

        

        st.divider()

        st.subheader("Data from PostgreSQL")

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )