import pandas as pd


def validate_dataframe(
    df: pd.DataFrame,
) -> dict:
    """
    Validate the final DataFrame before migration.
    """

    errors = []

    warnings = []


    # =========================================
    # EMPTY DATASET
    # =========================================

    if df.empty:

        errors.append(
            "Dataset is empty."
        )


    # =========================================
    # COLUMN CHECK
    # =========================================

    if len(df.columns) == 0:

        errors.append(
            "Dataset has no columns."
        )


    # =========================================
    # NULL VALUES
    # =========================================

    null_count = int(
        df.isna().sum().sum()
    )

    if null_count > 0:

        warnings.append(
            f"Dataset contains {null_count} null values."
        )


    # =========================================
    # DUPLICATES
    # =========================================

    duplicate_count = int(
        df.duplicated().sum()
    )

    if duplicate_count > 0:

        warnings.append(
            f"Dataset contains {duplicate_count} duplicate rows."
        )


    # =========================================
    # COLUMN NAMES
    # =========================================

    invalid_columns = []

    for column in df.columns:

        if not str(column).strip():

            invalid_columns.append(
                str(column)
            )


    if invalid_columns:

        errors.append(
            "Dataset contains empty column names."
        )




    valid = len(errors) == 0


    return {

        "valid": valid,

        "message": (
            "Dataset is ready for migration."
            if valid
            else "Dataset failed validation."
        ),

        "errors": errors,

        "warnings": warnings,

        "rows": int(len(df)),

        "columns": int(len(df.columns)),

        "null_values": null_count,

        "duplicate_rows": duplicate_count,

    }