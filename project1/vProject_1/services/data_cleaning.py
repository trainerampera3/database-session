import io
import re
from pathlib import Path

import pandas as pd
import streamlit as st


CHUNK_SIZE = 50000


TARGET_COLUMNS = {
    "companies": [
        "corporate_identification_number",
        "company_name",
        "company_status",
        "company_class",
        "company_category",
        "company_sub_category",
        "registration_date",
        "registered_state",
        "authorized_cap",
        "paidup_capital",
        "industrial_class",
        "business_activity",
        "registered_office_address",
        "registrar_of_companies",
        "email_addr",
        "latest_year_annual_return",
        "latest_year_financial_statement",
    ],
    "startup_funding": [
        "startup_name",
        "city",
        "state",
        "sector",
        "funding_stage",
        "funding_amount",
        "funding_date",
        "investor_name",
        "source",
    ],
    "state_policies": [
        "state",
        "policy_name",
        "sector",
        "incentive_type",
        "incentive_description",
        "eligibility",
        "benefit",
        "effective_from",
        "effective_to",
        "source",
    ],
    "office_market": [
        "city",
        "state",
        "locality",
        "property_type",
        "rent_per_sqft",
        "rent_per_sqm",
        "vacancy_rate",
        "availability",
        "market_date",
        "source",
    ],
}


DATASET_TABLES = {
    "companies": "companies",
    "startup_funding": "startup_funding",
    "state_policies": "state_policies",
    "office_market": "office_market",
}


def normalize_missing_values(df):
    missing_values = [
        "",
        " ",
        "nan",
        "NaN",
        "NAN",
        "null",
        "NULL",
        "None",
        "none",
        "N/A",
        "n/a",
        "NA",
        "na",
        "-",
        "--",
    ]

    for column in df.columns:
        if pd.api.types.is_object_dtype(df[column]) or pd.api.types.is_string_dtype(df[column]):
            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
                .replace(missing_values, pd.NA)
            )

    return df


def trim_text_values(df):
    for column in df.columns:
        if pd.api.types.is_object_dtype(df[column]) or pd.api.types.is_string_dtype(df[column]):
            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    return df


def canonicalize_columns(df):
    renamed = {}

    for column in df.columns:
        name = str(column).strip()

        if name.lower().startswith("unnamed:"):
            renamed[column] = None
            continue

        normalized = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()
        renamed[column] = normalized

    keep_columns = [column for column in df.columns if renamed[column] is not None]
    df = df[keep_columns].copy()

    df.columns = [renamed[column] for column in keep_columns]

    return merge_duplicate_columns(df)


def merge_duplicate_columns(df):
    if not df.columns.duplicated().any():
        return df

    result = pd.DataFrame(index=df.index)

    for column in dict.fromkeys(df.columns):
        same_columns = df.loc[:, df.columns == column]

        if same_columns.shape[1] == 1:
            result[column] = same_columns.iloc[:, 0]
        else:
            merged = same_columns.iloc[:, 0].copy()

            for index in range(1, same_columns.shape[1]):
                merged = merged.combine_first(
                    same_columns.iloc[:, index]
                )

            result[column] = merged

    return result


def add_missing_columns(df, columns):
    for column in columns:
        if column not in df.columns:
            df[column] = pd.NA

    return df


def clean_company_dates(df):
    if "date_of_registration" not in df.columns:
        return df

    values = (
        df["date_of_registration"]
        .astype("string")
        .str.strip()
    )

    parsed = pd.to_datetime(
        values,
        errors="coerce",
        dayfirst=True,
    )

    df["registration_date"] = parsed.dt.date

    return df


def clean_company_years(df):
    for source_column, target_column in [
        (
            "latest_year_annual_return",
            "latest_year_annual_return",
        ),
        (
            "latest_year_financial_statement",
            "latest_year_financial_statement",
        ),
    ]:
        if source_column not in df.columns:
            continue

        values = (
            df[source_column]
            .astype("string")
            .str.strip()
        )

        year_from_date = values.str.extract(
            r"(?:^|[-/])(\d{4})$",
            expand=False,
        )

        year_anywhere = values.str.extract(
            r"(\d{4})",
            expand=False,
        )

        extracted = year_from_date.combine_first(
            year_anywhere
        )

        df[target_column] = pd.to_numeric(
            extracted,
            errors="coerce",
        ).astype("Int64")

    return df


def clean_numeric_column(df, column):
    if column not in df.columns:
        return df

    values = (
        df[column]
        .astype("string")
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.strip()
    )

    df[column] = pd.to_numeric(
        values,
        errors="coerce",
    )

    return df


def clean_company_data(df):
    if "authorized_capital" in df.columns and "authorized_cap" not in df.columns:
        df["authorized_cap"] = df["authorized_capital"]

    if "paid_up_capital" in df.columns and "paidup_capital" not in df.columns:
        df["paidup_capital"] = df["paid_up_capital"]

    if "email" in df.columns and "email_addr" not in df.columns:
        df["email_addr"] = df["email"]
    if "authorized_capital" in df.columns and "authorized_cap" not in df.columns:
        df["authorized_cap"] = df["authorized_capital"]

    if "paid_up_capital" in df.columns and "paidup_capital" not in df.columns:
        df["paidup_capital"] = df["paid_up_capital"]

    if "email" in df.columns and "email_addr" not in df.columns:
        df["email_addr"] = df["email"]
    if "authorized_cap" in df.columns:
        df = clean_numeric_column(df, "authorized_cap")

    if "paidup_capital" in df.columns:
        df = clean_numeric_column(df, "paidup_capital")

    if "industrial_class" in df.columns:
        values = (
            df["industrial_class"]
            .astype("string")
            .str.strip()
        )

        numeric = pd.to_numeric(
            values,
            errors="coerce",
        )

        df["industrial_class"] = (
            numeric
            .round()
            .astype("Int64")
            .astype("string")
        )

    df = clean_company_dates(df)
    df = clean_company_years(df)

    if "principal_business_activity_as_per_cin" in df.columns:
        df["business_activity"] = (
            df["principal_business_activity_as_per_cin"]
            .astype("string")
            .str.strip()
        )

    return df


def clean_startup_data(df):
    if "startup" in df.columns and "startup_name" not in df.columns:
        df["startup_name"] = df["startup"]
    elif "company_name" in df.columns and "startup_name" not in df.columns:
        df["startup_name"] = df["company_name"]

    if "date" in df.columns and "funding_date" not in df.columns:
        df["funding_date"] = df["date"]

    if "investor" in df.columns and "investor_name" not in df.columns:
        df["investor_name"] = df["investor"]

    if "startup" in df.columns and "startup_name" not in df.columns:
        df["startup_name"] = df["startup"]
    elif "company_name" in df.columns and "startup_name" not in df.columns:
        df["startup_name"] = df["company_name"]

    if "date" in df.columns and "funding_date" not in df.columns:
        df["funding_date"] = df["date"]

    if "investor" in df.columns and "investor_name" not in df.columns:
        df["investor_name"] = df["investor"]
    if "industry_vertical" in df.columns:
        df["sector"] = (
            df["industry_vertical"]
            .astype("string")
            .str.strip()
        )

    if "investment_type" in df.columns:
        df["funding_stage"] = (
            df["investment_type"]
            .astype("string")
            .str.strip()
        )

    if "amount_usd_numeric" in df.columns:
        df["funding_amount"] = pd.to_numeric(
            df["amount_usd_numeric"],
            errors="coerce",
        )
    elif "amount_usd" in df.columns:
        amount = (
            df["amount_usd"]
            .astype("string")
            .str.replace(",", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.strip()
        )

        df["funding_amount"] = pd.to_numeric(
            amount,
            errors="coerce",
        )

    if "investors" in df.columns:
        df["investor_name"] = (
            df["investors"]
            .astype("string")
            .str.strip()
        )

    if "funding_date" in df.columns:
        df["funding_date"] = pd.to_datetime(
            df["funding_date"],
            errors="coerce",
            dayfirst=True,
        ).dt.date

    for column in ["city", "state", "startup_name", "sector", "funding_stage"]:
        if column in df.columns:
            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    return df


def clean_policy_data(df):
    if "policy_period" in df.columns:
        period = (
            df["policy_period"]
            .astype("string")
            .str.strip()
        )

        years = period.str.extract(
            r"(\d{4})\s*-\s*(\d{4})"
        )

        df["effective_from"] = pd.to_datetime(
            years[0] + "-01-01",
            errors="coerce",
        ).dt.date

        df["effective_to"] = pd.to_datetime(
            years[1] + "-12-31",
            errors="coerce",
        ).dt.date

    benefit_columns = [
        "funding_incentive",
        "tax_incentive",
        "land_support",
        "power_support",
        "employment_training_support",
        "market_incubation_support",
        "compliance_support",
        "other_benefits",
    ]

    available = [
        column
        for column in benefit_columns
        if column in df.columns
    ]

    if available:
        def combine_benefits(row):
            values = []

            for column in available:
                value = row[column]

                if pd.isna(value):
                    continue

                value = str(value).strip()

                if value:
                    values.append(value)

            if not values:
                return pd.NA

            return " | ".join(values)

        df["benefit"] = df.apply(
            combine_benefits,
            axis=1,
        )

    return df


def clean_office_data(df):
    if "market_area" in df.columns and "locality" not in df.columns:
        df["locality"] = df["market_area"]

    if "office_grade" in df.columns and "property_type" not in df.columns:
        df["property_type"] = df["office_grade"]

    if "market_date" not in df.columns and "data_period" in df.columns:
        df["market_date"] = df["data_period"]

    for column in ["locality", "property_type"]:
        if column in df.columns:
            df[column] = df[column].astype("string").str.strip()

    minimum = None
    maximum = None

    if "rent_min_inr_per_sqft_month" in df.columns:
        minimum = pd.to_numeric(
            df["rent_min_inr_per_sqft_month"],
            errors="coerce",
        )

    if "rent_max_inr_per_sqft_month" in df.columns:
        maximum = pd.to_numeric(
            df["rent_max_inr_per_sqft_month"],
            errors="coerce",
        )

    if minimum is not None and maximum is not None:
        df["rent_per_sqft"] = minimum.add(maximum).div(2)
        df.loc[minimum.notna() & maximum.isna(), "rent_per_sqft"] = minimum[minimum.notna() & maximum.isna()]
        df.loc[minimum.isna() & maximum.notna(), "rent_per_sqft"] = maximum[minimum.isna() & maximum.notna()]
    elif minimum is not None:
        df["rent_per_sqft"] = minimum
    elif maximum is not None:
        df["rent_per_sqft"] = maximum

    if "rent_per_sqft" in df.columns:
        df["rent_per_sqft"] = pd.to_numeric(df["rent_per_sqft"], errors="coerce")
        df["rent_per_sqm"] = df["rent_per_sqft"] * 10.7639

    if "market_date" in df.columns:
        period = df["market_date"].astype("string").str.strip().str.upper()
        quarter_map = {
            "Q1": "01-01",
            "Q2": "04-01",
            "Q3": "07-01",
            "Q4": "10-01",
        }

        def convert_period(value):
            if pd.isna(value):
                return pd.NaT

            text = str(value).strip().upper()
            match = re.match(r"^(Q[1-4])\s+(\d{4})$", text)

            if match:
                quarter = match.group(1)
                year = match.group(2)
                return pd.to_datetime(
                    f"{year}-{quarter_map[quarter]}",
                    errors="coerce",
                )

            return pd.to_datetime(
                text,
                errors="coerce",
                dayfirst=True,
            )

        df["market_date"] = period.apply(convert_period)

    return df


def normalize_business_key_value(value):
    if pd.isna(value):
        return None

    value = str(value).strip().lower()

    if not value:
        return None

    return value


def remove_duplicates(df, dataset_type, seen_keys=None):
    keys = {
        "companies": [
            "corporate_identification_number",
        ],
        "startup_funding": [
            "startup_name",
            "funding_date",
            "funding_amount",
            "city",
        ],
        "state_policies": [
            "state",
            "policy_name",
            "sector",
        ],
        "office_market": [
            "city",
            "state",
            "locality",
            "property_type",
            "market_date",
        ],
    }

    key_columns = [
        column
        for column in keys.get(dataset_type, [])
        if column in df.columns
    ]

    if not key_columns:
        return df

    if seen_keys is None:
        seen_keys = set()

    keep_indexes = []

    for index, values in df[key_columns].iterrows():
        normalized = tuple(
            normalize_business_key_value(value)
            for value in values
        )

        if dataset_type == "companies":
            cin = normalized[0]

            if cin is None:
                keep_indexes.append(index)
                continue

            if cin in seen_keys:
                continue

            seen_keys.add(cin)
            keep_indexes.append(index)
            continue

        if all(value is None for value in normalized):
            keep_indexes.append(index)
            continue

        if normalized in seen_keys:
            continue

        seen_keys.add(normalized)
        keep_indexes.append(index)

    return df.loc[keep_indexes].copy()


def select_target_columns(df, dataset_type):
    target_columns = TARGET_COLUMNS.get(
        dataset_type,
        [],
    )

    df = add_missing_columns(
        df,
        target_columns,
    )

    return df[target_columns].copy()


def clean_uploaded_file(
    file,
    dataset_type,
    options,
):
    if hasattr(file, "seek"):
        file.seek(0)

    reader = pd.read_csv(
        file,
        chunksize=CHUNK_SIZE,
        low_memory=False,
    )

    output = io.BytesIO()
    first_chunk = True
    seen_keys = set()

    for chunk in reader:
        chunk = canonicalize_columns(chunk)

        if options.get("normalize_missing", True):
            chunk = normalize_missing_values(chunk)

        if options.get("trim_text", True):
            chunk = trim_text_values(chunk)

        if dataset_type == "companies":
            chunk = clean_company_data(chunk)

        elif dataset_type == "startup_funding":
            chunk = clean_startup_data(chunk)

        elif dataset_type == "state_policies":
            chunk = clean_policy_data(chunk)

        elif dataset_type == "office_market":
            chunk = clean_office_data(chunk)

        if options.get("duplicates", True):
            chunk = remove_duplicates(
                chunk,
                dataset_type,
                seen_keys,
            )

        chunk = select_target_columns(
            chunk,
            dataset_type,
        )

        chunk.to_csv(
            output,
            index=False,
            header=first_chunk,
        )

        first_chunk = False

    output.seek(0)

    return output


def detect_dataset_type(file_name):
    name = file_name.lower()

    if "registered" in name or "company" in name:
        return "companies"

    if "startup" in name or "funding" in name:
        return "startup_funding"

    if "policy" in name or "incentive" in name:
        return "state_policies"

    if "office" in name or "market" in name:
        return "office_market"

    return "unknown"


def percentage(value, total):
    if total == 0:
        return 0.0

    return round(
        (value / total) * 100,
        2,
    )


def analyse_missing_values(file):
    file.seek(0)

    total_rows = 0
    missing_counts = None
    columns = []

    for chunk in pd.read_csv(
        file,
        chunksize=CHUNK_SIZE,
        low_memory=False,
    ):
        if not columns:
            columns = list(chunk.columns)
            missing_counts = pd.Series(
                0,
                index=columns,
                dtype="int64",
            )

        total_rows += len(chunk)

        missing_counts = (
            missing_counts
            .add(
                chunk.isna().sum(),
                fill_value=0,
            )
            .astype("int64")
        )

    file.seek(0)

    missing = {}

    if missing_counts is not None:
        for column in columns:
            count = int(
                missing_counts[column]
            )

            missing[column] = {
                "count": count,
                "percentage": percentage(
                    count,
                    total_rows,
                ),
            }

    return total_rows, columns, missing


def analyse_date_columns(file, dataset_type):
    file.seek(0)

    candidates = {
        "companies": [
            "DATE_OF_REGISTRATION",
        ],
        "startup_funding": [
            "funding_date",
        ],
        "office_market": [
            "data_period",
        ],
        "state_policies": [
            "policy_period",
        ],
    }

    columns_to_check = candidates.get(
        dataset_type,
        [],
    )

    invalid = {}
    totals = {}

    for chunk in pd.read_csv(
        file,
        chunksize=CHUNK_SIZE,
        low_memory=False,
    ):
        for column in columns_to_check:
            if column not in chunk.columns:
                continue

            values = (
                chunk[column]
                .dropna()
                .astype(str)
                .str.strip()
            )

            totals[column] = (
                totals.get(column, 0)
                + len(values)
            )

            if column == "policy_period":
                valid_mask = values.str.match(
                    r"^\d{4}\s*-\s*\d{4}$"
                )

            elif column == "data_period":
                valid_mask = values.str.match(
                    r"^Q[1-4]\s+\d{4}$",
                    case=False,
                )

            else:
                valid_mask = pd.to_datetime(
                    values,
                    errors="coerce",
                    dayfirst=True,
                ).notna()

            invalid_count = int(
                (~valid_mask).sum()
            )

            invalid[column] = (
                invalid.get(column, 0)
                + invalid_count
            )

    file.seek(0)

    result = {}

    for column, count in invalid.items():
        result[column] = {
            "count": count,
            "percentage": percentage(
                count,
                totals.get(column, 0),
            ),
        }

    return result


def analyse_numeric_columns(file, dataset_type):
    file.seek(0)

    candidates = {
        "companies": [
            "INDUSTRIAL_CLASS",
            "LATEST_YEAR_ANNUAL_RETURN",
            "LATEST_YEAR_FINANCIAL_STATEMENT",
            "AUTHORIZED_CAP",
            "PAIDUP_CAPITAL",
        ],
        "startup_funding": [
            "amount_usd_numeric",
            "amount_usd",
        ],
        "office_market": [
            "rent_min_inr_per_sqft_month",
            "rent_max_inr_per_sqft_month",
        ],
    }

    columns_to_check = candidates.get(
        dataset_type,
        [],
    )

    invalid = {}
    totals = {}

    for chunk in pd.read_csv(
        file,
        chunksize=CHUNK_SIZE,
        low_memory=False,
    ):
        for column in columns_to_check:
            if column not in chunk.columns:
                continue

            values = (
                chunk[column]
                .dropna()
                .astype(str)
                .str.strip()
            )

            totals[column] = (
                totals.get(column, 0)
                + len(values)
            )

            if column in [
                "LATEST_YEAR_ANNUAL_RETURN",
                "LATEST_YEAR_FINANCIAL_STATEMENT",
            ]:
                valid = values.str.contains(
                    r"\d{4}",
                    regex=True,
                )

            else:
                cleaned = (
                    values
                    .str.replace(",", "", regex=False)
                    .str.replace("₹", "", regex=False)
                    .str.replace("$", "", regex=False)
                )

                valid = pd.to_numeric(
                    cleaned,
                    errors="coerce",
                ).notna()

            invalid_count = int(
                (~valid).sum()
            )

            invalid[column] = (
                invalid.get(column, 0)
                + invalid_count
            )

    file.seek(0)

    result = {}

    for column, count in invalid.items():
        result[column] = {
            "count": count,
            "percentage": percentage(
                count,
                totals.get(column, 0),
            ),
        }

    return result


def analyse_duplicates(file, dataset_type):
    file.seek(0)

    key_columns = {
        "companies": [
            "CORPORATE_IDENTIFICATION_NUMBER",
        ],
        "startup_funding": [
            "startup_name",
            "funding_date",
            "amount_usd_numeric",
            "city",
        ],
        "state_policies": [
            "state",
            "policy_name",
            "sector",
        ],
        "office_market": [
            "city",
            "state",
            "market_area",
            "office_grade",
            "data_period",
        ],
    }

    keys = key_columns.get(
        dataset_type,
        [],
    )

    if not keys:
        file.seek(0)

        return {
            "count": 0,
            "percentage": 0,
        }

    seen = set()
    duplicate_count = 0
    total_rows = 0

    for chunk in pd.read_csv(
        file,
        chunksize=CHUNK_SIZE,
        low_memory=False,
    ):
        available = [
            column
            for column in keys
            if column in chunk.columns
        ]

        if not available:
            continue

        for values in chunk[
            available
        ].itertuples(
            index=False,
            name=None,
        ):
            normalized = tuple(
                normalize_business_key_value(
                    value
                )
                for value in values
            )

            if dataset_type == "companies":
                total_rows += 1

                cin = normalized[0]

                if cin is None:
                    continue

                if cin in seen:
                    duplicate_count += 1
                else:
                    seen.add(cin)

            else:
                total_rows += 1

                if all(
                    value is None
                    for value in normalized
                ):
                    continue

                if normalized in seen:
                    duplicate_count += 1
                else:
                    seen.add(normalized)

    file.seek(0)

    return {
        "count": duplicate_count,
        "percentage": percentage(
            duplicate_count,
            total_rows,
        ),
    }


def analyse_uploaded_file(file):
    try:
        dataset_type = detect_dataset_type(
            file.name
        )

        (
            total_rows,
            columns,
            missing,
        ) = analyse_missing_values(file)

        date_issues = analyse_date_columns(
            file,
            dataset_type,
        )

        numeric_issues = analyse_numeric_columns(
            file,
            dataset_type,
        )

        duplicates = analyse_duplicates(
            file,
            dataset_type,
        )

        return {
            "status": "success",
            "dataset_type": dataset_type,
            "file_name": file.name,
            "row_count": total_rows,
            "column_count": len(columns),
            "rows": total_rows,
            "columns": columns,
            "missing": missing,
            "date_issues": date_issues,
            "numeric_issues": numeric_issues,
            "duplicates": duplicates,
            "quality_report": pd.DataFrame(
                [
                    {
                        "Column": column,
                        "Missing": details.get("count", 0),
                        "Missing %": details.get(
                            "percentage",
                            0,
                        ),
                    }
                    for column, details in missing.items()
                ]
            ),
        }

    except Exception as error:
        return {
            "status": "failed",
            "file_name": file.name,
            "error": str(error),
            "rows": 0,
            "columns": [],
        }


def get_quality_summary(analysis):
    missing = analysis.get(
        "missing",
        {},
    )

    columns_with_nulls = sum(
        1
        for value in missing.values()
        if isinstance(value, dict)
        and value.get("count", 0) > 0
    )

    columns_with_empty_values = 0

    return {
        "rows": analysis.get(
            "row_count",
            analysis.get("rows", 0),
        ),
        "columns": analysis.get(
            "column_count",
            len(analysis.get("columns", [])),
        ),
        "duplicate_rows": analysis.get(
            "duplicates",
            {},
        ).get(
            "count",
            0,
        ),
        "columns_with_nulls": columns_with_nulls,
        "columns_with_empty_values": columns_with_empty_values,
    }


def generate_cleaning_options(analysis):
    dataset_type = analysis.get(
        "dataset_type"
    )

    options = []

    missing = analysis.get(
        "missing",
        {},
    )

    missing_total = sum(
        item.get("count", 0)
        for item in missing.values()
        if isinstance(item, dict)
    )

    options.append(
        {
            "key": "normalize_missing",
            "label": "Normalize missing values",
            "details": (
                f"{missing_total:,} missing or blank values detected."
            ),
            "description": (
                "Convert common missing markers to NULL."
            ),
            "recommended": True,
        }
    )

    options.append(
        {
            "key": "trim_text",
            "label": "Trim text values",
            "details": "Remove unnecessary spaces from text fields.",
            "description": "Standardize text before migration.",
            "recommended": True,
        }
    )

    if dataset_type == "companies":
        options.extend(
            [
                {
                    "key": "company_dates",
                    "label": "Normalize registration dates",
                    "details": "Convert registration dates to PostgreSQL DATE.",
                    "description": "Handles DD-MM-YYYY and other valid date formats.",
                    "recommended": True,
                },
                {
                    "key": "company_years",
                    "label": "Convert financial years",
                    "details": "Convert values such as 31-03-2017 to integer 2017.",
                    "description": "Invalid year values become NULL.",
                    "recommended": True,
                },
                {
                    "key": "industrial_class",
                    "label": "Normalize industrial class",
                    "details": "Normalize industrial classification values.",
                    "description": "Invalid numeric values become NULL.",
                    "recommended": True,
                },
            ]
        )

    elif dataset_type == "startup_funding":
        options.append(
            {
                "key": "startup_fields",
                "label": "Standardize funding fields",
                "details": "Prepare sector, stage, amount, investor and date fields.",
                "description": "Create database-ready funding fields.",
                "recommended": True,
            }
        )

    elif dataset_type == "state_policies":
        options.append(
            {
                "key": "policy_fields",
                "label": "Prepare policy dates and benefits",
                "details": "Convert policy periods and combine benefit fields.",
                "description": "Create database-ready policy fields.",
                "recommended": True,
            }
        )

    elif dataset_type == "office_market":
        options.append(
            {
                "key": "office_fields",
                "label": "Prepare office market values",
                "details": "Calculate average rent and convert quarterly periods.",
                "description": "Create locality, property type, rent and market date fields.",
                "recommended": True,
            }
        )

    duplicate_info = analysis.get(
        "duplicates",
        {},
    )

    duplicate_count = duplicate_info.get(
        "count",
        0,
    ) if isinstance(duplicate_info, dict) else 0

    options.append(
        {
            "key": "duplicates",
            "label": "Remove duplicate records",
            "details": (
                f"{duplicate_count:,} duplicate business-key rows detected."
            ),
            "description": (
                "Remove duplicate business keys across the complete file, "
                "including duplicates occurring in different CSV chunks."
            ),
            "recommended": True,
        }
    )

    return options


def _get_uploaded_lookup(uploaded_files):
    lookup = {}

    for file in uploaded_files:
        name = getattr(
            file,
            "name",
            None,
        )

        if name:
            lookup[name] = file

    return lookup


def _write_cleaned_file(cleaned_file, output_path):
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    cleaned_file.seek(0)

    with output_path.open(
        "wb"
    ) as destination:
        destination.write(
            cleaned_file.read()
        )


def _count_csv_rows(path):
    total = 0

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
    ) as source:
        next(
            source,
            None,
        )

        for _ in source:
            total += 1

    return total


def clean_all_datasets(
    analyses,
    cleaning_options,
    uploaded_files=None,
):
    if uploaded_files is None:
        uploaded_files = st.session_state.get(
            "uploaded_files",
            [],
        )

    uploaded_lookup = _get_uploaded_lookup(
        uploaded_files
    )

    base_dir = (
        Path(__file__)
        .resolve()
        .parents[1]
    )

    cleaned_dir = (
        base_dir
        / "data"
        / "cleaned"
    )

    cleaned_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    cleaned_files = {}
    results = {}

    for file_name, analysis in analyses.items():
        original_file = uploaded_lookup.get(
            file_name
        )

        if original_file is None:
            results[file_name] = {
                "status": "failed",
                "error": "Original uploaded file not found.",
            }
            continue

        try:
            dataset_type = analysis.get(
                "dataset_type"
            )

            options = cleaning_options.get(
                file_name,
                {},
            )

            if not isinstance(options, dict):
                options = {}

            cleaned_file = clean_uploaded_file(
                original_file,
                dataset_type,
                options,
            )

            # Write exactly one canonical cleaned file per dataset.
            # The mapping stage reads data/cleaned/<original filename>.csv.
            # This also prevents an older timestamped cleaned file from
            # being selected by the mapping stage.
            output_path = cleaned_dir / file_name

            stem = Path(file_name).stem

            for old_file in cleaned_dir.glob(f"{stem}*.csv"):
                if old_file != output_path:
                    try:
                        old_file.unlink()
                    except OSError:
                        pass

            _write_cleaned_file(
                cleaned_file,
                output_path,
            )

            row_count = _count_csv_rows(
                output_path
            )

            target_table = DATASET_TABLES.get(
                dataset_type
            )

            cleaned_files[file_name] = {
                "path": str(output_path),
                "rows": row_count,
                "target_table": target_table,
                "dataset_type": dataset_type,
            }

            results[file_name] = {
                "status": "success",
                "rows": row_count,
                "path": str(output_path),
            }

        except Exception as error:
            results[file_name] = {
                "status": "failed",
                "error": str(error),
            }

    st.session_state.cleaned_files = cleaned_files
    st.session_state.cleaning_results = results

    return results


def render_data_cleaning():
    analyses = st.session_state.get(
        "analyses",
        {},
    )

    uploaded_files = st.session_state.get(
        "uploaded_files",
        [],
    )

    if not analyses:
        st.warning(
            "No analysed datasets are available."
        )
        return

    st.markdown(
        "## Data cleaning"
    )

    all_cleaning_options = {}

    for file_name, analysis in analyses.items():
        dataset_type = analysis.get(
            "dataset_type",
            "unknown",
        )

        st.markdown(
            f"### {file_name}"
        )

        st.caption(
            f"Dataset type: {dataset_type}"
        )

        option_list = generate_cleaning_options(
            analysis
        )

        selected = {}

        for option in option_list:
            if not isinstance(option, dict):
                continue

            key = option.get(
                "key"
            )

            if not key:
                continue

            label = option.get(
                "label",
                key,
            )

            selected[key] = st.checkbox(
                label,
                value=bool(
                    option.get(
                        "recommended",
                        False,
                    )
                ),
                key=(
                    f"clean_{file_name}_{key}"
                ),
            )

            details = option.get(
                "details"
            )

            if details:
                st.caption(
                    details
                )

        all_cleaning_options[file_name] = selected

        st.divider()

    st.session_state.cleaning_options = (
        all_cleaning_options
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Back to analysis",
            use_container_width=True,
        ):
            st.session_state.upload_stage = 2
            st.rerun()

    with col2:
        if st.button(
            "Clean datasets",
            type="primary",
            use_container_width=True,
        ):
            results = clean_all_datasets(
                analyses,
                all_cleaning_options,
                uploaded_files,
            )

            failed = [
                file_name
                for file_name, result in results.items()
                if result.get("status") != "success"
            ]

            if failed:
                st.error(
                    "Cleaning failed for: "
                    + ", ".join(failed)
                )
            else:
                st.session_state.cleaning_done = True
                st.session_state.upload_stage = 4
                st.success(
                    "All datasets cleaned successfully."
                )
                st.rerun()
