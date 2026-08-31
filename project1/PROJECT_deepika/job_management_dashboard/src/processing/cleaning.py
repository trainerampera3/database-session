import pandas as pd

SALARY_RANGES = {
    "Entry": (30000, 50000),
    "Mid": (50000, 70000),
    "Senior": (70000, 100000),
    "Lead": (100001, 300000),
}


def clean_spaces(df):
    df = df.copy()
    for column in df.columns:
        if (
            df[column].dtype == "object"
            or pd.api.types.is_string_dtype(df[column])
        ):
            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )
    return df


def clean_duplicates(df):
    df=df.drop_duplicates()
    return df

def remove_null_rows(df):
    df=df.dropna()
    return df


def clean_capitalization(df):
    df = df.copy()
    if "experience_level" not in df.columns:
        return df
    values = (
        df["experience_level"]
        .astype("string")
        .str.strip()
        .str.lower()
    )
    mapping = {
        "entry": "Entry",
        "junior": "Entry",
        "jr": "Entry",
        "mid": "Mid",
        "middle": "Mid",
        "intermediate": "Mid",
        "senior": "Senior",
        "sr": "Senior",
        "lead": "Lead",
        "leader": "Lead",
        "unknown": pd.NA,
        "n/a": pd.NA,
        "none": pd.NA,
        "": pd.NA,
        "intern": pd.NA,
        "internship": pd.NA,
        "associate": pd.NA,
        "manager": pd.NA,
        "principal": pd.NA,
        "executive": pd.NA,
        "contract": pd.NA,
        "freelance": pd.NA,
    }

    df["experience_level"] = values.map(mapping)
    valid_levels = {"entry", "mid", "senior", "lead"}
    df.loc[~df["experience_level"].astype("string").str.strip().str.lower().isin(valid_levels),
        "experience_level"
    ] = pd.NA
    return df



def clean_remote_work(df):
    df = df.copy()
    if "remote_work" not in df.columns:
        return df
    values = (
        df["remote_work"]
        .astype("string")
        .str.strip()
        .str.lower()
    )
    mapping = {
        "fully remote": "Fully Remote",
        "remote": "Fully Remote",
        "remote friendly": "Fully Remote",
        "hybrid": "Hybrid",
        "on-site": "On-site",
        "onsite": "On-site",
        "on site": "On-site",
        "in-office": "On-site",
        "in office": "On-site",
        "office": "On-site",
        "unknown": pd.NA,
        "n/a": pd.NA,
        "na": pd.NA,
        "none": pd.NA,
        "not specified": pd.NA,
        "not_available": pd.NA,
        "": pd.NA,
    }
    df["remote_work"] = values.map(mapping)
    valid_remote_values = {"fully remote", "hybrid", "on-site"}
    df.loc[
        ~df["remote_work"].astype("string").str.strip().str.lower().isin(valid_remote_values),
        "remote_work"
    ] = pd.NA
    return df

def clean_numeric_columns(df):
    df = df.copy()
    numeric_columns = [
        "years_of_experience",
        "annual_salary_usd",
        "salary_min_usd",
        "salary_max_usd",
        "ai_salary_premium_pct",
        "posting_year",
        "posting_month",
    ]
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )
    return df



def clean_experience(df):
    df = df.copy()
    if "years_of_experience" not in df.columns:
        return df
    df["years_of_experience"] = pd.to_numeric(
        df["years_of_experience"],
        errors="coerce"
    )
    df.loc[
        df["years_of_experience"] < 0,
        "years_of_experience"
    ] = pd.NA

    def get_level(years):
        if pd.isna(years):
            return pd.NA

        if years <= 3:
            return "Entry"

        elif years <= 8:
            return "Mid"

        elif years <= 12:
            return "Senior"

        else:
            return "Lead"

    valid_levels = {"entry", "mid", "senior", "lead"}

    if "experience_level" in df.columns:
        normalized_current = (
            df["experience_level"]
            .astype("string")
            .str.strip()
            .str.lower()
        )

    return df



def clean_salary(df):
    df = df.copy()
    if "annual_salary_usd" not in df.columns:
        return df
    if "experience_level" not in df.columns:
        return df
    df["annual_salary_usd"] = pd.to_numeric(
        df["annual_salary_usd"],
        errors="coerce"
    ).astype("float64")
    for level, salary_range in SALARY_RANGES.items():
        minimum, maximum = salary_range
        mask = (
            df["experience_level"]
            .eq(level)
        )
        invalid = (
            df["annual_salary_usd"].isna()
            |
            (df["annual_salary_usd"] < minimum)
            |
            (df["annual_salary_usd"] > maximum)
        )
        midpoint = float(
            (minimum + maximum) / 2
        )
        df.loc[
            mask & invalid,
            "annual_salary_usd"
        ] = midpoint
    return df



def clean_salary_range(df):
    df = df.copy()
    if "experience_level" not in df.columns:
        return df
    if "salary_min_usd" in df.columns:

        df["salary_min_usd"] = pd.to_numeric(
            df["salary_min_usd"],
            errors="coerce"
        ).astype("float64")

    if "salary_max_usd" in df.columns:

        df["salary_max_usd"] = pd.to_numeric(
            df["salary_max_usd"],
            errors="coerce"
        ).astype("float64")

    for level, salary_range in SALARY_RANGES.items():

        minimum, maximum = salary_range
        level_mask = df["experience_level"].eq(level)

        if "salary_min_usd" in df.columns:
            invalid_min = (
                df["salary_min_usd"].isna()
                | (df["salary_min_usd"] < minimum)
            )
            df.loc[level_mask & invalid_min, "salary_min_usd"] = float(minimum)

        if "salary_max_usd" in df.columns:
            invalid_max = (
                df["salary_max_usd"].isna()
                | (df["salary_max_usd"] > maximum)
            )
            df.loc[level_mask & invalid_max, "salary_max_usd"] = float(maximum)

    return df



def clean_ai_salary_premium(df):
    df = df.copy()
    if "ai_salary_premium_pct" not in df.columns:
        return df

    df["ai_salary_premium_pct"] = pd.to_numeric(
        df["ai_salary_premium_pct"],
        errors="coerce"
    ).astype("float64")
    invalid = (
        df["ai_salary_premium_pct"].isna()
        |
        (df["ai_salary_premium_pct"] < 0)
        |
        (df["ai_salary_premium_pct"] > 100)
    )
    df.loc[
        invalid,
        "ai_salary_premium_pct"
    ] = 10.0

    df["ai_salary_premium_pct"] = (
        df["ai_salary_premium_pct"]
        .clip(0, 100)
        .astype("float64")
    )
    return df

def clean_posting_month(df):
    df = df.copy()
    if "posting_month" not in df.columns:
        return df
    df["posting_month"] = pd.to_numeric(
        df["posting_month"],
        errors="coerce"
    )
    invalid = (
        df["posting_month"].isna()
        |
        (df["posting_month"] < 1)
        |
        (df["posting_month"] > 12)
    )
    df.loc[
        invalid,
        "posting_month"
    ] = 1

    df["posting_month"] = (
        df["posting_month"]
        .clip(1, 12)
        .round()
        .astype("int64")
    )

    return df


def clean_boolean_columns(df):
    df = df.copy()

    boolean_columns = [
        "is_senior",
        "is_remote_friendly",
        "is_llm_role",
    ]
    mapping = {
        "yes": 1,
        "y": 1,
        "true": 1,
        "1": 1,

        "no": 0,
        "n": 0,
        "false": 0,
        "0": 0,
    }
    for column in boolean_columns:

        if column not in df.columns:
            continue

        values = (
            df[column]
            .astype("string")
            .str.strip()
            .str.lower()
        )
        df[column] = values.map(mapping)

        df[column] = (
            pd.to_numeric(
                df[column],
                errors="coerce"
            )
            .fillna(0)
            .astype("int64")
        )
    return df



def clean_null_values(df):
    df = df.copy()
    
    text_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns
    for column in text_columns:
        if column == "remote_work":
            df[column] = df[column].fillna(pd.NA)
            continue

        mode_values = df[column].mode(
            dropna=True
        )
        if not mode_values.empty:

            df[column] = df[column].fillna(
                mode_values.iloc[0]
            )
        else:
            df[column] = df[column].fillna(
                "Unknown"
            )
    

    numeric_columns = df.select_dtypes(
        include=["number"]
    ).columns

    for column in numeric_columns:

        if df[column].isna().any():

            median_value = df[column].median()

            if pd.notna(median_value):

                df[column] = df[column].fillna(
                    median_value
                )

            else:

                df[column] = df[column].fillna(0)

    return df





def clean_dataset(df):

    cleaned_df = df.copy()

    original_rows = len(cleaned_df)

    cleaned_df = clean_spaces(cleaned_df)

     
    before_duplicates = len(cleaned_df)

    cleaned_df = clean_duplicates(cleaned_df)

    duplicates_removed = (
        before_duplicates - len(cleaned_df)
    )


    cleaned_df = clean_capitalization(cleaned_df)

    cleaned_df = clean_remote_work(cleaned_df)

    cleaned_df = clean_numeric_columns(cleaned_df)

    cleaned_df = clean_experience(cleaned_df)

    cleaned_df = clean_salary(cleaned_df)

    cleaned_df = clean_salary_range(cleaned_df)

    cleaned_df = clean_ai_salary_premium(cleaned_df)

    cleaned_df = clean_posting_month(cleaned_df)

    cleaned_df = clean_boolean_columns(cleaned_df)


    before_nulls = len(cleaned_df)

    cleaned_df = remove_null_rows(cleaned_df)

    null_rows_removed = (
        before_nulls - len(cleaned_df)
    )

    
    cleaned_df = clean_spaces(cleaned_df)

    
    print("\n====================================")
    print("CLEANING COMPLETED")
    print("====================================")

    print(f"Original rows: {original_rows}")
    print(f"Duplicate rows removed: {duplicates_removed}")
    print(f"NULL rows removed: {null_rows_removed}")
    print(f"Final valid rows: {len(cleaned_df)}")

    return cleaned_df

