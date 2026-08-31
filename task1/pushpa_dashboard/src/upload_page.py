import streamlit as st
import pandas as pd


def show_upload_data():

    st.header("Upload Data")

    st.write(
        "Upload, analyse, clean and prepare railway datasets "
        "for database migration."
    )

    # ---------- Stepper Style ----------

    st.markdown("""
    <style>
    .step-line {
        height: 2px;
        background: #444;
        margin-top: 16px;
    }

    .step-number {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        border: 2px solid #666;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: auto;
        font-weight: 700;
    }

    .step-active {
        background: #d62828;
        border-color: #d62828;
        color: white;
    }

    .step-complete {
        background: #555;
        border-color: #777;
        color: white;
    }

    .step-label {
        text-align: center;
        margin-top: 8px;
        font-size: 13px;
    }
    </style>
    """, unsafe_allow_html=True)

    steps = [
        "Upload CSV",
        "Analyse",
        "Clean",
        "Map Columns",
        "Migrate"
    ]

    if "upload_page" not in st.session_state:
        st.session_state.upload_page = "Upload CSV"

    current_step = steps.index(
        st.session_state.upload_page
    )

    # ---------- Stepper ----------

    step_columns = st.columns(9)

    for i, step in enumerate(steps):

        with step_columns[i * 2]:

            if i == current_step:
                circle_class = "step-number step-active"

            elif i < current_step:
                circle_class = "step-number step-complete"

            else:
                circle_class = "step-number"

            st.markdown(
                f"""
                <div class="{circle_class}">
                    {i + 1}
                </div>
                <div class="step-label">
                    {step}
                </div>
                """,
                unsafe_allow_html=True
            )

        if i < len(steps) - 1:

            with step_columns[i * 2 + 1]:

                st.markdown(
                    '<div class="step-line"></div>',
                    unsafe_allow_html=True
                )

    st.divider()

   
    # UPLOAD CSV
    
    if st.session_state.upload_page == "Upload CSV":

        left, center, right = st.columns([1, 3, 1])

        with center:

            with st.container(border=True):

                st.markdown(
                    "<h2 style='text-align:center;'>"
                    "Import Railway Dataset"
                    "</h2>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    """
                    <p style="
                        text-align:center;
                        color:#aaaaaa;
                    ">
                    Upload your railway CSV files to begin
                    the data preparation process.
                    </p>
                    """,
                    unsafe_allow_html=True
                )

                uploaded_files = st.file_uploader(
                    "Drop railway CSV files here",
                    type=["csv", "tsv"],
                    accept_multiple_files=True,
                    key="railway_files"
                )

                st.caption(
                    "CSV / TSV · UTF-8 · First row treated as header"
                )

                if uploaded_files:

                    uploaded_data = {}

                    for uploaded_file in uploaded_files:

                        if uploaded_file.name.endswith(".tsv"):

                            df = pd.read_csv(
                                uploaded_file,
                                sep="\t"
                            )

                        else:

                            df = pd.read_csv(
                                uploaded_file
                            )

                        uploaded_data[
                            uploaded_file.name
                        ] = df

                    st.session_state.uploaded_data = uploaded_data

                    st.markdown("### Uploaded Files")

                    for filename, df in uploaded_data.items():

                        col1, col2, col3, col4 = st.columns(4)

                        col1.write(f"**{filename}**")
                        col2.write(f"Rows: {len(df):,}")
                        col3.write(f"Columns: {len(df.columns)}")
                        col4.success("Uploaded")

                    if st.button(
                        "Upload Files",
                        key="confirm_upload"
                    ):

                        st.session_state.files_uploaded = True

                        st.success(
                            "Railway files uploaded successfully."
                        )

    
    # ANALYSE
    
    elif st.session_state.upload_page == "Analyse":

        st.subheader("Analyse Railway Data")

        if "uploaded_data" not in st.session_state:

            st.info(
                "Please upload the railway files first."
            )

        else:

            for filename, df in (
                st.session_state.uploaded_data.items()
            ):

                st.markdown(f"### {filename}")

                col1, col2, col3, col4 = st.columns(4)

                col1.metric("Rows", f"{len(df):,}")
                col2.metric("Columns", len(df.columns))
                col3.metric(
                    "Missing Values",
                    int(df.isna().sum().sum())
                )
                col4.metric(
                    "Duplicate Rows",
                    int(df.duplicated().sum())
                )

                st.dataframe(
                    df.head(10),
                    use_container_width=True
                )

   

    elif st.session_state.upload_page == "Clean":

        st.subheader("Clean Railway Data")

        if "uploaded_data" not in st.session_state:

            st.info(
                "Please upload the railway files first."
            )

        else:

            duplicate_count = sum(
                int(df.duplicated().sum())
                for df in st.session_state.uploaded_data.values()
            )

            missing_count = sum(
                int(df.isna().sum().sum())
                for df in st.session_state.uploaded_data.values()
            )

            empty_count = sum(
                int(df.isna().all(axis=1).sum())
                for df in st.session_state.uploaded_data.values()
            )

            text_count = sum(
                len(
                    df.select_dtypes(
                        include=["object", "string"]
                    ).columns
                )
                for df in st.session_state.uploaded_data.values()
            )

            st.markdown("### Cleaning Options")

            remove_duplicates = st.checkbox(
                f"Remove duplicate rows ({duplicate_count:,} found)",
                value=duplicate_count > 0,
                key="remove_duplicates"
            )

            handle_missing = st.checkbox(
                f"Handle missing values ({missing_count:,} found)",
                value=missing_count > 0,
                key="handle_missing"
            )

            remove_empty = st.checkbox(
                f"Remove empty rows ({empty_count:,} found)",
                value=empty_count > 0,
                key="remove_empty"
            )

            standardize_text = st.checkbox(
                f"Standardize text ({text_count:,} columns)",
                value=text_count > 0,
                key="standardize_text"
            )

            st.divider()

            if st.button(
                "Apply Cleaning",
                key="apply_cleaning"
            ):

                cleaned_data = {}

                for filename, df in (
                    st.session_state.uploaded_data.items()
                ):

                    clean_df = df.copy()

                    if remove_duplicates:
                        clean_df = clean_df.drop_duplicates()

                    if remove_empty:
                        clean_df = clean_df.dropna(
                            how="all"
                        )

                    if handle_missing:

                        text_columns = clean_df.select_dtypes(
                            include=["object", "string"]
                        ).columns

                        for column in text_columns:
                            clean_df[column] = (
                                clean_df[column].fillna("")
                            )

                    if standardize_text:

                        text_columns = clean_df.select_dtypes(
                            include=["object", "string"]
                        ).columns

                        for column in text_columns:

                            clean_df[column] = (
                                clean_df[column]
                                .astype("string")
                                .str.strip()
                            )

                    cleaned_data[filename] = clean_df

                st.session_state.cleaned_data = cleaned_data

                st.success(
                    "Data cleaning completed successfully."
                )

            if "cleaned_data" in st.session_state:

                st.subheader("Cleaning Summary")

                for filename, df in (
                    st.session_state.cleaned_data.items()
                ):

                    st.write(
                        f"**{filename}** — "
                        f"{len(df):,} rows remaining"
                    )

                st.subheader(
                    "Cleaned Dataset Preview"
                )

                for filename, df in (
                    st.session_state.cleaned_data.items()
                ):

                    st.write(f"**{filename}**")

                    st.dataframe(
                        df.head(10),
                        use_container_width=True
                    )

   
    # MAP COLUMNS
    

    elif st.session_state.upload_page == "Map Columns":

        st.subheader("Map Columns")

        data_source = st.session_state.get(
            "cleaned_data",
            st.session_state.get(
                "uploaded_data",
                {}
            )
        )

        if not data_source:

            st.info(
                "Please upload and clean the railway data first."
            )

        else:

            st.write(
                "Review the railway columns before migration."
            )

            for filename, df in data_source.items():

                st.markdown(f"### {filename}")

                mapping = pd.DataFrame({
                    "Railway Column": df.columns,
                    "PostgreSQL Status": [
                        "Ready"
                        for column in df.columns
                    ]
                })

                st.dataframe(
                    mapping,
                    use_container_width=True,
                    hide_index=True
                )

            st.success(
                "✓ Mapping is ready for migration."
            )

           

    elif st.session_state.upload_page == "Migrate":

        st.subheader("Migrate Railway Data")

        if "migration_report" not in st.session_state:

            st.write(
                "Start the migration of your cleaned railway data."
            )

            if st.button(
                "Start Migration",
                key="start_migration"
            ):

                from batch_migration import migrate_data

                progress = st.progress(0)
                status = st.empty()

                status.info(
                    "🚆 Preparing railway data..."
                )
                progress.progress(20)

                status.info(
                    "📦 Migrating train information..."
                )
                progress.progress(40)

                status.info(
                    "🛤️ Migrating train schedules..."
                )
                progress.progress(60)

                status.info(
                    "🗄️ Saving data to PostgreSQL..."
                )
                progress.progress(80)

                report = migrate_data()

                progress.progress(100)

                status.success(
                    "✓ Migration completed successfully!"
                )

                st.session_state.migration_report = report

                st.rerun()

        else:

            report = st.session_state.migration_report

            st.success(
                "✓ Migration Completed"
            )

            st.subheader(
                "Migration Report"
            )

            col1, col2, col3, col4, col5 = st.columns(5)

            col1.metric(
                "Status",
                report["status"]
            )

            col2.metric(
                "Files",
                report["files"]
            )

            col3.metric(
                "Rows Migrated",
                f'{report["total_rows"]:,}'
            )

            col4.metric(
                "Duration",
                report["duration"]
            )

            col5.metric(
                "Result",
                report["result"]
            )
        
    
    # BOTTOM NAVIGATION
    

    st.divider()

    current_index = steps.index(
        st.session_state.upload_page
    )

    back_col, spacer, next_col = st.columns([1, 5, 1])

    # ---------- Back ----------

    with back_col:

        if current_index == 0:

            if st.button(
                "← Back",
                key="back_upload"
            ):

                st.session_state.main_page = "Dashboard"
                st.rerun()

        elif current_index == 1:

            if st.button(
                "← Back: Upload CSV",
                key="back_analyse"
            ):

                st.session_state.upload_page = "Upload CSV"
                st.rerun()

        elif current_index == 2:

            if st.button(
                "← Back: Analyse",
                key="back_clean"
            ):

                st.session_state.upload_page = "Analyse"
                st.rerun()

        elif current_index == 3:

            if st.button(
                "← Back: Clean",
                key="back_mapping"
            ):

                st.session_state.upload_page = "Clean"
                st.rerun()

        elif current_index == 4:

            if st.button(
                "← Back to Map Columns",
                key="back_migrate"
            ):

                st.session_state.upload_page = "Map Columns"
                st.rerun()

    # ---------- Next ----------

    with next_col:

        if current_index == 0:

            if st.button(
                "Next: Analyse →",
                key="next_upload"
            ):

                st.session_state.upload_page = "Analyse"
                st.rerun()

        elif current_index == 1:

            if st.button(
                "Next: Clean →",
                key="next_analyse"
            ):

                st.session_state.upload_page = "Clean"
                st.rerun()

        elif current_index == 2:

            if st.button(
                "Next: Map Columns →",
                key="next_clean"
            ):

                st.session_state.upload_page = "Map Columns"
                st.rerun()

        elif current_index == 3:

            if st.button(
                "Start Migration →",
                key="next_mapping"
            ):

                st.session_state.upload_page = "Migrate"
                st.rerun()

        elif current_index == 4:

            if st.session_state.get(
                "migration_report"
            ):

                if st.button(
                    "Go to Dashboard →",
                    key="next_report"
                ):

                    st.session_state.main_page = "Dashboard"
                    st.rerun()