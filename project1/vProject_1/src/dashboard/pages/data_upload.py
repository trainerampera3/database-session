import streamlit as st

from project1.vProject_1.services.data_quality import analyse_uploaded_file


MAX_FILES = 4
MAX_FILE_SIZE_MB = 500
MAX_TOTAL_SIZE_GB = 1


# Validate uploaded files.
def validate_files(files):
    if len(files) > MAX_FILES:
        return False, (
            f"Maximum {MAX_FILES} files are allowed."
        )

    total_size = sum(
        file.size
        for file in files
    )

    for file in files:
        size_mb = file.size / (1024 * 1024)

        if size_mb > MAX_FILE_SIZE_MB:
            return False, (
                f"{file.name} exceeds the "
                f"{MAX_FILE_SIZE_MB} MB limit."
            )

    total_size_gb = (
        total_size
        / (1024 * 1024 * 1024)
    )

    if total_size_gb > MAX_TOTAL_SIZE_GB:
        return False, (
            f"Total upload size is "
            f"{total_size_gb:.2f} GB. "
            f"Maximum is {MAX_TOTAL_SIZE_GB} GB."
        )

    return True, ""


# Render the upload stage.
def render_data_upload():
    st.markdown("### Upload data")

    st.caption(
        "Maximum 4 CSV files, 500 MB per file and 1 GB total."
    )

    files = st.file_uploader(
        "Select CSV files",
        type=["csv"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if not files:
        return

    valid, message = validate_files(files)

    if not valid:
        st.error(message)
        return

    st.session_state.uploaded_files = files

    st.markdown("### Selected files")

    total_size = 0

    for file in files:
        size_mb = file.size / (1024 * 1024)
        total_size += file.size

        col1, col2 = st.columns([4, 1])

        with col1:
            st.write(file.name)

        with col2:
            st.write(f"{size_mb:.2f} MB")

    total_size_gb = (
        total_size
        / (1024 * 1024 * 1024)
    )

    st.caption(
        f"{len(files)} file(s) selected | "
        f"{total_size_gb:.2f} GB total"
    )

    if st.button(
        "Start analysis",
        use_container_width=True
    ):
        analyses = {}

        progress = st.progress(0)
        status = st.empty()

        for index, file in enumerate(files):
            status.write(
                f"Analysing {file.name}..."
            )

            analyses[file.name] = (
                analyse_uploaded_file(file)
            )

            progress.progress(
                (index + 1) / len(files)
            )

        st.session_state.analyses = analyses
        st.session_state.analysis_done = True
        st.session_state.upload_stage = 2

        st.rerun()