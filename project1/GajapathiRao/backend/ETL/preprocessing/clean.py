import pandas as pd


VALID_MISSING_ACTIONS = {
    None,
    "none",
    "drop",
    "mean",
    "median",
    "zero",
}


def clean_dataframe(
    df: pd.DataFrame,
    missing_action: str = "none",
    remove_duplicates: bool = False,
) -> pd.DataFrame:

    processed_df = df.copy()



    if missing_action not in VALID_MISSING_ACTIONS:

        raise ValueError(
            "Invalid missing value action."
        )



    if missing_action == "drop":

        processed_df = processed_df.dropna()

    elif missing_action == "mean":

        numeric_columns = (
            processed_df
            .select_dtypes(include="number")
            .columns
        )

        for column in numeric_columns:

            processed_df[column] = (
                processed_df[column]
                .fillna(
                    processed_df[column].mean()
                )
            )

    elif missing_action == "median":

        numeric_columns = (
            processed_df
            .select_dtypes(include="number")
            .columns
        )

        for column in numeric_columns:

            processed_df[column] = (
                processed_df[column]
                .fillna(
                    processed_df[column].median()
                )
            )

    elif missing_action == "zero":

        numeric_columns = (
            processed_df
            .select_dtypes(include="number")
            .columns
        )

        for column in numeric_columns:

            processed_df[column] = (
                processed_df[column]
                .fillna(0)
            )


    if remove_duplicates:

        processed_df = (
            processed_df
            .drop_duplicates()
            .reset_index(drop=True)
        )

    return processed_df