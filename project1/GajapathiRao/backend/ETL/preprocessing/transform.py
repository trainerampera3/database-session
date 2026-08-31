import pandas as pd


def rename_columns(
    df: pd.DataFrame,
    rename_map: dict | None = None,
) -> pd.DataFrame:

    if not rename_map:
        return df

    processed_df = df.copy()

    processed_df = processed_df.rename(
        columns=rename_map
    )

    return processed_df


def remove_columns(
    df: pd.DataFrame,
    columns: list[str] | None = None,
) -> pd.DataFrame:

    if not columns:
        return df

    processed_df = df.copy()

    existing_columns = [
        column
        for column in columns
        if column in processed_df.columns
    ]

    processed_df = processed_df.drop(
        columns=existing_columns
    )

    return processed_df


def convert_column_types(
    df: pd.DataFrame,
    type_map: dict | None = None,
) -> pd.DataFrame:

    if not type_map:
        return df

    processed_df = df.copy()

    for column, data_type in type_map.items():

        if column not in processed_df.columns:
            continue

        if data_type == "integer":

            processed_df[column] = pd.to_numeric(
                processed_df[column],
                errors="coerce"
            ).astype("Int64")

        elif data_type == "float":

            processed_df[column] = pd.to_numeric(
                processed_df[column],
                errors="coerce"
            )

        elif data_type == "string":

            processed_df[column] = (
                processed_df[column]
                .astype("string")
            )

        elif data_type == "date":

            processed_df[column] = pd.to_datetime(
                processed_df[column],
                errors="coerce"
            )

        else:

            raise ValueError(
                f"Unsupported data type: {data_type}"
            )

    return processed_df


def apply_transformations(
    df: pd.DataFrame,
    rename_map: dict | None = None,
    remove_columns_list: list[str] | None = None,
    type_map: dict | None = None,
) -> pd.DataFrame:

    processed_df = df.copy()

    processed_df = rename_columns(
        processed_df,
        rename_map
    )

    processed_df = remove_columns(
        processed_df,
        remove_columns_list
    )

    processed_df = convert_column_types(
        processed_df,
        type_map
    )

    return processed_df