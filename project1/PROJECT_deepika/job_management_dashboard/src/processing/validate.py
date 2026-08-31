import pandas as pd

REQUIRED_COLUMNS = [
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


def expected_experience_level(years):

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


def validate_dataset(df):

    errors = []
    

    if df is None:

        return {
            "valid": False,
            "error_count": 1,
            "errors": [
                "Dataset is None."
            ]
        }

    if len(df) == 0:

        return {
            "valid": False,
            "error_count": 1,
            "errors": [
                "Dataset contains no records."
            ]
        }
    

    for column in REQUIRED_COLUMNS:

        if column not in df.columns:

            errors.append(
                f"Required column missing: {column}"
            )

    # If required columns are missing, stop here
    if errors:

        return {
            "valid": False,
            "error_count": len(errors),
            "errors": errors
        }

    

    for index, row in df.iterrows():

        years = row["years_of_experience"]

        actual_level = str(
            row["experience_level"]
        ).strip()

        expected_level = expected_experience_level(
            years
        )

        if actual_level != expected_level:

            errors.append(
                f"Row {index + 1}: "
                f"{years} years of experience "
                f"should be {expected_level}, "
                f"found {actual_level}"
            )

    

    invalid_experience = (
        pd.to_numeric(
            df["years_of_experience"],
            errors="coerce"
        ) < 0
    )

    invalid_count = int(
        invalid_experience.sum()
    )

    if invalid_count > 0:

        errors.append(
            f"{invalid_count} negative "
            f"years_of_experience values found."
        )

    
    invalid_month = (
        pd.to_numeric(
            df["posting_month"],
            errors="coerce"
        ).isna()
        |
        (
            pd.to_numeric(
                df["posting_month"],
                errors="coerce"
            ) < 1
        )
        |
        (
            pd.to_numeric(
                df["posting_month"],
                errors="coerce"
            ) > 12
        )
    )

    invalid_month_count = int(
        invalid_month.sum()
    )

    if invalid_month_count > 0:

        errors.append(
            f"{invalid_month_count} invalid "
            f"posting_month values found."
        )

    

    premium = pd.to_numeric(
        df["ai_salary_premium_pct"],
        errors="coerce"
    )

    invalid_premium = (
        premium.isna()
        |
        (premium < 0)
        |
        (premium > 100)
    )

    invalid_premium_count = int(
        invalid_premium.sum()
    )

    if invalid_premium_count > 0:

        errors.append(
            f"{invalid_premium_count} invalid "
            f"ai_salary_premium_pct values found."
        )

    
    salary = pd.to_numeric(
        df["annual_salary_usd"],
        errors="coerce"
    )

    invalid_salary = (
        salary.isna()
        |
        (salary < 0)
    )

    invalid_salary_count = int(
        invalid_salary.sum()
    )

    if invalid_salary_count > 0:

        errors.append(
            f"{invalid_salary_count} invalid "
            f"annual_salary_usd values found."
        )
    
    demand_score = pd.to_numeric(
        df["demand_score"],
        errors="coerce"
    )

    invalid_demand = (
        demand_score.isna()
        |
        (demand_score < 0)
    )

    invalid_demand_count = int(
        invalid_demand.sum()
    )

    if invalid_demand_count > 0:

        errors.append(
            f"{invalid_demand_count} invalid "
            f"demand_score values found."
        )

    
    return {
        "valid": len(errors) == 0,
        "error_count": len(errors),
        "errors": errors
    }