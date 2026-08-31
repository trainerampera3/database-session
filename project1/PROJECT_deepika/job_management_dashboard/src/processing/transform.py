import pandas as pd

TARGET_COLUMNS = [
    "job_id",
    "job_title",
    "job_category",
    "experience_level",
    "years_of_experience",
    "education_required",
    "annual_salary_usd",
    "salary_min_usd",
    "salary_max_usd",
    "city",
    "country",
    "remote_work",
    "company_size",
    "industry",
    "required_skills",
    "ai_salary_premium_pct",
    "demand_score",
    "demand_growth_yoy_pct",
    "benefits_score_10",
    "posting_year",
    "posting_month",
    "is_senior",
    "is_remote_friendly",
    "is_llm_role",
]


NUMERIC_COLUMNS = [
    "annual_salary_usd",
    "salary_min_usd",
    "salary_max_usd",
    "ai_salary_premium_pct",
    "demand_growth_yoy_pct",
    "benefits_score_10",
]

INTEGER_COLUMNS = [
    "years_of_experience",
    "demand_score",
    "posting_year",
    "posting_month",
]

BOOLEAN_COLUMNS = [
    "is_senior",
    "is_remote_friendly",
    "is_llm_role",
]

def remove_duplicates(df):
    df = df.copy()
    before = len(df)
    df = (
        df
        .drop_duplicates()
        .reset_index(drop=True)
    )
    removed = before - len(df)

    print(
        f"Duplicate rows removed: {removed}"
    )
    return df

def remove_null_rows(df):
    df = df.copy()
    before = len(df)
    df = (
        df
        .dropna()
        .reset_index(drop=True)
    )
    removed = before - len(df)
    print(
        f"NULL rows removed: {removed}"
    )

    return df



def apply_column_mapping(
    df,
    column_mapping=None
):
    df = df.copy()
    if column_mapping:
        df = df.rename(
            columns=column_mapping
        )
    return df


def convert_numeric_types(df):
    df = df.copy()
    for column in NUMERIC_COLUMNS:
        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


def convert_integer_types(df):

    df = df.copy()

    for column in INTEGER_COLUMNS:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

            df[column] = (
                df[column]
                .round()
                .astype("Int64")
            )

    return df



def transform_experience_level(df):

    df = df.copy()

    if "years_of_experience" not in df.columns:
        return df

    def get_level(years):

        if pd.isna(years):
            return "Entry"

        if years <= 3:
            return "Entry"

        elif years <= 8:
            return "Mid"

        elif years <= 12:
            return "Senior"

        else:
            return "Lead"

    df["experience_level"] = (
        df["years_of_experience"]
        .apply(get_level)
    )

    return df



def convert_boolean_types(df):

    df = df.copy()

    for column in BOOLEAN_COLUMNS:

        if column not in df.columns:
            continue

        
        df[column] = (
            pd.to_numeric(
                df[column],
                errors="coerce"
            )
            .fillna(0)
            .astype(bool)
        )

    return df



def arrange_columns(df):

    df = df.copy()

    existing_columns = [
        column
        for column in TARGET_COLUMNS
        if column in df.columns
    ]

    return df[existing_columns]




def transform_dataset(
    df,
    column_mapping=None
):

    transformed_df = df.copy()

    original_rows = len(transformed_df)

    transformed_df = remove_duplicates(
        transformed_df
    )

    rows_after_duplicates = len(
        transformed_df
    )

    transformed_df = apply_column_mapping(
        transformed_df,
        column_mapping
    )
    transformed_df = convert_numeric_types(
        transformed_df
    )

    transformed_df = convert_integer_types(
        transformed_df
    )
    

    transformed_df = remove_null_rows(
        transformed_df
    )


    transformed_df = transform_experience_level(
        transformed_df
    )

    transformed_df = convert_boolean_types(
        transformed_df
    )


    transformed_df = arrange_columns(
        transformed_df
    )

    duplicates_removed = (
        original_rows
        - rows_after_duplicates
    )

    null_rows_removed = (
        rows_after_duplicates
        - len(transformed_df)
    )

    print("\n====================================")
    print("TRANSFORMATION COMPLETED")
    print("====================================")

    print(
        f"Original rows: {original_rows}"
    )

    print(
        f"Duplicate rows removed: "
        f"{duplicates_removed}"
    )

    print(
        f"NULL rows removed: "
        f"{null_rows_removed}"
    )

    print(
        f"Final transformed rows: "
        f"{len(transformed_df)}"
    )

    return transformed_df

