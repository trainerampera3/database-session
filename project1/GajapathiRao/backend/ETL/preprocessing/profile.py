import pandas as pd


def profile_dataframe(df: pd.DataFrame) -> dict:
    """
    Generate a data-quality profile for a DataFrame.
    """

    column_details = []

    for column in df.columns:

        null_count = int(df[column].isna().sum())

        column_details.append(
            {
                "name": str(column),
                "dtype": str(df[column].dtype),
                "null_count": null_count,
                "null_percentage": round(
                    (null_count / len(df)) * 100,
                    2
                ) if len(df) > 0 else 0,
                "unique_count": int(
                    df[column].nunique(dropna=True)
                ),
            }
        )

    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "null_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "column_details": column_details,
    }


def get_preview(
    df: pd.DataFrame,
    rows: int = 20
) -> list:

    preview_df = df.head(rows).copy()

    preview_df = preview_df.astype(object)

    preview_df = preview_df.where(
        pd.notna(preview_df),
        None
    )

    return preview_df.to_dict(
        orient="records"
    )