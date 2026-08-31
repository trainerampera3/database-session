import pandas as pd
import streamlit as st

from services.data_quality import get_quality_summary


# Render analysis results for all uploaded datasets.
def render_data_analysis():

    st.markdown("### Data analysis")

    analyses = st.session_state.get(
        "analyses",
        {}
    )

    if not analyses:

        st.warning(
            "No analysis results are available."
        )

        if st.button(
            "Back to upload",
            use_container_width=True
        ):

            st.session_state.upload_stage = 1
            st.rerun()

        return

    successful = {
        name: result
        for name, result in analyses.items()
        if result.get("status") == "success"
    }

    failed = {
        name: result
        for name, result in analyses.items()
        if result.get("status") != "success"
    }

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Datasets analysed",
            len(successful)
        )

    with col2:
        st.metric(
            "Datasets with errors",
            len(failed)
        )

    st.markdown("### Analysis status")

    rows = []

    for name, result in analyses.items():

        if result.get("status") == "success":

            rows.append(
                {
                    "Dataset": name,
                    "Type": result.get(
                        "dataset_type",
                        "Unknown"
                    ),
                    "Status": "Completed",
                    "Rows": f"{result.get('row_count', 0):,}",
                    "Columns": result.get(
                        "column_count",
                        0
                    ),
                    "Error": ""
                }
            )

        else:

            rows.append(
                {
                    "Dataset": name,
                    "Type": "-",
                    "Status": "Failed",
                    "Rows": "-",
                    "Columns": "-",
                    "Error": result.get(
                        "error",
                        "Unknown error"
                    )
                }
            )

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True
    )

    if failed:

        for name, result in failed.items():

            st.error(
                f"{name}: {result.get('error', 'Unknown error')}"
            )

    if not successful:

        st.error(
            "No dataset could be analysed."
        )

    else:

        st.markdown("### Dataset details")

        selected = st.selectbox(
            "Select dataset",
            list(successful.keys())
        )

        analysis = successful[selected]

        summary = get_quality_summary(
            analysis
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Rows",
                f"{summary['rows']:,}"
            )

        with col2:
            st.metric(
                "Columns",
                summary["columns"]
            )

        with col3:
            st.metric(
                "Duplicate rows",
                f"{summary['duplicate_rows']:,}"
            )

        with col4:

            issues = (
                summary["columns_with_nulls"]
                + summary["columns_with_empty_values"]
            )

            st.metric(
                "Columns with issues",
                issues
            )

        st.markdown("### Column quality")

        st.dataframe(
            analysis["quality_report"],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### Date issues")

        date_rows = []

        for column, result in analysis.get(
            "date_issues",
            {}
        ).items():

            date_rows.append(
                {
                    "Column": column,
                    "Invalid values": result["count"],
                    "Invalid %": result["percentage"]
                }
            )

        if date_rows:

            st.dataframe(
                pd.DataFrame(date_rows),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.success(
                "No date issues detected."
            )

        st.markdown("### Numeric issues")

        numeric_rows = []

        for column, result in analysis.get(
            "numeric_issues",
            {}
        ).items():

            numeric_rows.append(
                {
                    "Column": column,
                    "Invalid values": result["count"],
                    "Invalid %": result["percentage"]
                }
            )

        if numeric_rows:

            st.dataframe(
                pd.DataFrame(numeric_rows),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.success(
                "No numeric issues detected."
            )

        # st.markdown("### Dataset columns")

        # st.dataframe(
        #     pd.DataFrame(
        #         {
        #             "Column": analysis["columns"]
        #         }
        #     ),
        #     use_container_width=True,
        #     hide_index=True
        # )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Back to upload",
            use_container_width=True
        ):

            st.session_state.upload_stage = 1
            st.rerun()

    with col2:

        if st.button(
            "Continue to cleaning",
            use_container_width=True
        ):

            st.session_state.upload_stage = 3
            st.rerun()