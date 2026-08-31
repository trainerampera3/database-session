import io
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


CHUNK_SIZE = 50000


# Normalize column names only for internal matching.
def normalize_column_name(column):
    return (
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
    )


# Find a source column using case-insensitive matching.
def find_column(df, names):
    normalized = {
        normalize_column_name(column): column
        for column in df.columns
    }

    for name in names:
        key = normalize_column_name(name)

        if key in normalized:
            return normalized[key]

    return None


# Convert common missing markers into pandas NULL.
def normalize_missing_values(df):
    missing_values = {
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
        "unknown",
        "Unknown",
        "UNKNOWN",
    }

    for column in df.columns:
        if (
            pd.api.types.is_object_dtype(df[column])
            or pd.api.types.is_string_dtype(df[column])
        ):
            series = (
                df[column]
                .astype("string")
                .str.strip()
            )

            df[column] = series.replace(
                list(missing_values),
                pd.NA,
            )

    return df


# Trim unnecessary whitespace from text values.
def trim_text_values(df):
    for column in df.columns:
        if (
            pd.api.types.is_object_dtype(df[column])
            or pd.api.types.is_string_dtype(df[column])
        ):
            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    return df


# Convert values to numeric safely.
def clean_numeric_series(series):
    values = (
        series
        .astype("string")
        .str.strip()
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("%", "", regex=False)
    )

    return pd.to_numeric(
        values,
        errors="coerce",
    )


# Convert dates safely.
def clean_date_series(series):
    values = (
        series
        .astype("string")
        .str.strip()
    )

    values = values.replace(
        [
            "",
            "nan",
            "NaN",
            "N/A",
            "NA",
            "null",
            "None",
        ],
        pd.NA,
    )

    converted = pd.to_datetime(
        values,
        errors="coerce",
        dayfirst=False,
    )

    return converted.dt.strftime("%Y-%m-%d")


# Clean company registration dates.
def clean_company_dates(df):
    column = find_column(
        df,
        [
            "DATE_OF_REGISTRATION",
            "date_of_registration",
            "registration_date",
        ],
    )

    if column is None:
        return df

    df["registration_date"] = clean_date_series(
        df[column]
    )

    return df


# Clean company financial year fields.
def clean_company_years(df):
    source_columns = [
        (
            "LATEST_YEAR_ANNUAL_RETURN",
            "latest_year_annual_return",
        ),
        (
            "LATEST_YEAR_FINANCIAL_STATEMENT",
            "latest_year_financial_statement",
        ),
    ]

    for source_name, target_name in source_columns:
        column = find_column(
            df,
            [
                source_name,
                target_name,
            ],
        )

        if column is None:
            continue

        values = (
            df[column]
            .astype("string")
            .str.strip()
        )

        extracted = values.str.extract(
            r"((?:19|20)\d{2})",
            expand=False,
        )

        df[target_name] = pd.to_numeric(
            extracted,
            errors="coerce",
        ).astype("Int64")

    return df


# Clean company numeric and text fields.
def clean_company_data(df):
    text_mapping = {
        "CORPORATE_IDENTIFICATION_NUMBER":
            "corporate_identification_number",
        "COMPANY_NAME":
            "company_name",
        "COMPANY_STATUS":
            "company_status",
        "COMPANY_CLASS":
            "company_class",
        "COMPANY_CATEGORY":
            "company_category",
        "COMPANY_SUB_CATEGORY":
            "company_sub_category",
        "REGISTERED_STATE":
            "registered_state",
        "BUSINESS_ACTIVITY":
            "business_activity",
        "REGISTERED_OFFICE_ADDRESS":
            "registered_office_address",
        "REGISTRAR_OF_COMPANIES":
            "registrar_of_companies",
        "EMAIL_ADDR":
            "email_addr",
    }

    for source_name, target_name in text_mapping.items():
        column = find_column(
            df,
            [
                source_name,
                target_name,
            ],
        )

        if column is not None:
            df[target_name] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    numeric_mapping = {
        "AUTHORIZED_CAP": "authorized_cap",
        "PAIDUP_CAPITAL": "paidup_capital",
    }

    for source_name, target_name in numeric_mapping.items():
        column = find_column(
            df,
            [
                source_name,
                target_name,
            ],
        )

        if column is not None:
            df[target_name] = clean_numeric_series(
                df[column]
            )

    industrial_column = find_column(
        df,
        [
            "INDUSTRIAL_CLASS",
            "industrial_class",
        ],
    )

    if industrial_column is not None:
        values = (
            df[industrial_column]
            .astype("string")
            .str.strip()
        )

        numeric_values = clean_numeric_series(
            values
        )

        df["industrial_class"] = (
            numeric_values
            .round()
            .astype("Int64")
            .astype("string")
        )

        original_text = values.notna()

        df.loc[
            original_text
            & numeric_values.isna(),
            "industrial_class"
        ] = values[
            original_text
            & numeric_values.isna()
        ]

    clean_company_dates(df)
    clean_company_years(df)

    return df


# Clean startup funding data.
def clean_startup_data(df):
    direct_mapping = {
        "startup_name": [
            "startup_name",
            "startup",
            "company_name",
        ],
        "city": [
            "city",
            "location",
        ],
        "state": [
            "state",
        ],
        "sector": [
            "sector",
            "industry_vertical",
            "industry",
        ],
        "funding_stage": [
            "funding_stage",
            "investment_type",
            "funding_type",
        ],
        "investor_name": [
            "investor_name",
            "investors",
            "investor",
        ],
        "source": [
            "source",
        ],
    }

    for target, candidates in direct_mapping.items():
        column = find_column(
            df,
            candidates,
        )

        if column is not None:
            df[target] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    amount_column = find_column(
        df,
        [
            "funding_amount",
            "amount_usd_numeric",
            "amount_usd",
            "amount",
        ],
    )

    if amount_column is not None:
        df["funding_amount"] = clean_numeric_series(
            df[amount_column]
        )

    date_column = find_column(
        df,
        [
            "funding_date",
            "date",
        ],
    )

    if date_column is not None:
        df["funding_date"] = clean_date_series(
            df[date_column]
        )

    return df


# Clean state policy data.
def clean_policy_data(df):
    direct_mapping = {
        "state": [
            "state",
        ],
        "policy_name": [
            "policy_name",
            "policy",
            "policy_title",
        ],
        "sector": [
            "sector",
        ],
        "incentive_type": [
            "incentive_type",
        ],
        "incentive_description": [
            "incentive_description",
            "description",
        ],
        "eligibility": [
            "eligibility",
        ],
        "source": [
            "source",
        ],
    }

    for target, candidates in direct_mapping.items():
        column = find_column(
            df,
            candidates,
        )

        if column is not None:
            df[target] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    period_column = find_column(
        df,
        [
            "policy_period",
            "effective_period",
        ],
    )

    if period_column is not None:
        period = (
            df[period_column]
            .astype("string")
            .str.strip()
        )

        year_range = period.str.extract(
            r"((?:19|20)\d{2})\s*[-–]\s*((?:19|20)\d{2})",
            expand=True,
        )

        df["effective_from"] = (
            year_range[0]
            + "-01-01"
        )

        df["effective_to"] = (
            year_range[1]
            + "-12-31"
        )

        single_year = period.str.extract(
            r"^((?:19|20)\d{2})$",
            expand=False,
        )

        df.loc[
            single_year.notna()
            & df["effective_from"].isna(),
            "effective_from"
        ] = (
            single_year
            + "-01-01"
        )

        df.loc[
            single_year.notna()
            & df["effective_to"].isna(),
            "effective_to"
        ] = (
            single_year
            + "-12-31"
        )

    benefit_columns = [
        "funding_incentive",
        "tax_incentive",
        "land_support",
        "power_support",
        "employment_training_support",
        "market_incubation_support",
        "compliance_support",
        "other_benefits",
        "benefit",
    ]

    available = []

    for name in benefit_columns:
        column = find_column(
            df,
            [name],
        )

        if column is not None:
            available.append(column)

    if available:

        def combine_benefits(row):
            values = []

            for column in available:
                value = row[column]

                if pd.isna(value):
                    continue

                text = str(value).strip()

                if text:
                    values.append(text)

            if not values:
                return pd.NA

            return " | ".join(
                dict.fromkeys(values)
            )

        df["benefit"] = df.apply(
            combine_benefits,
            axis=1,
        )

    return df


# Clean office market data.
def clean_office_data(df):
    city_column = find_column(
        df,
        [
            "city",
        ],
    )

    if city_column is not None:
        df["city"] = (
            df[city_column]
            .astype("string")
            .str.strip()
        )

    state_column = find_column(
        df,
        [
            "state",
        ],
    )

    if state_column is not None:
        df["state"] = (
            df[state_column]
            .astype("string")
            .str.strip()
        )

    locality_column = find_column(
        df,
        [
            "locality",
            "market_area",
        ],
    )

    if locality_column is not None:
        df["locality"] = (
            df[locality_column]
            .astype("string")
            .str.strip()
        )

    property_column = find_column(
        df,
        [
            "property_type",
            "office_grade",
        ],
    )

    if property_column is not None:
        df["property_type"] = (
            df[property_column]
            .astype("string")
            .str.strip()
        )

    minimum_column = find_column(
        df,
        [
            "rent_min_inr_per_sqft_month",
            "rent_min_inr_per_sqft",
            "rent_min",
            "min_rent",
        ],
    )

    maximum_column = find_column(
        df,
        [
            "rent_max_inr_per_sqft_month",
            "rent_max_inr_per_sqft",
            "rent_max",
            "max_rent",
        ],
    )

    minimum = None
    maximum = None

    if minimum_column is not None:
        minimum = clean_numeric_series(
            df[minimum_column]
        )

    if maximum_column is not None:
        maximum = clean_numeric_series(
            df[maximum_column]
        )

    if minimum is not None and maximum is not None:
        both = minimum.notna() & maximum.notna()

        df["rent_per_sqft"] = pd.NA

        df.loc[
            both,
            "rent_per_sqft"
        ] = (
            minimum[both]
            + maximum[both]
        ) / 2

        only_min = (
            minimum.notna()
            & maximum.isna()
        )

        only_max = (
            minimum.isna()
            & maximum.notna()
        )

        df.loc[
            only_min,
            "rent_per_sqft"
        ] = minimum[only_min]

        df.loc[
            only_max,
            "rent_per_sqft"
        ] = maximum[only_max]

    elif minimum is not None:
        df["rent_per_sqft"] = minimum

    elif maximum is not None:
        df["rent_per_sqft"] = maximum

    existing_rent = find_column(
        df,
        [
            "rent_per_sqft",
        ],
    )

    if (
        existing_rent is not None
        and "rent_per_sqft" not in df.columns
    ):
        df["rent_per_sqft"] = clean_numeric_series(
            df[existing_rent]
        )

    if "rent_per_sqft" in df.columns:
        df["rent_per_sqm"] = (
            clean_numeric_series(
                df["rent_per_sqft"]
            ) * 10.7639
        )

    vacancy_column = find_column(
        df,
        [
            "vacancy_rate",
            "vacancy",
        ],
    )

    if vacancy_column is not None:
        df["vacancy_rate"] = clean_numeric_series(
            df[vacancy_column]
        )

    availability_column = find_column(
        df,
        [
            "availability",
            "available_area",
        ],
    )

    if availability_column is not None:
        df["availability"] = (
            df[availability_column]
            .astype("string")
            .str.strip()
        )

    market_date_column = find_column(
        df,
        [
            "market_date",
        ],
    )

    if market_date_column is not None:
        df["market_date"] = clean_date_series(
            df[market_date_column]
        )

    period_column = find_column(
        df,
        [
            "data_period",
            "market_period",
        ],
    )

    if period_column is not None:
        period = (
            df[period_column]
            .astype("string")
            .str.strip()
        )

        quarter_dates = {
            "Q1": "01-01",
            "Q2": "04-01",
            "Q3": "07-01",
            "Q4": "10-01",
        }

        def convert_quarter(value):
            if pd.isna(value):
                return pd.NA

            text = str(value).strip()

            match = re.search(
                r"\b(Q[1-4])\s*[- ]?\s*((?:19|20)\d{2})\b",
                text,
                flags=re.IGNORECASE,
            )

            if not match:
                return pd.NA

            quarter = match.group(1).upper()
            year = match.group(2)

            return (
                f"{year}-"
                f"{quarter_dates[quarter]}"
            )

        period_dates = period.apply(
            convert_quarter
        )

        if "market_date" not in df.columns:
            df["market_date"] = period_dates
        else:
            missing_market_date = (
                df["market_date"].isna()
            )

            df.loc[
                missing_market_date,
                "market_date"
            ] = period_dates[
                missing_market_date
            ]

    return df


# Remove duplicate rows using dataset business keys.
def remove_duplicates(df, dataset_type):
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

    selected_keys = []

    for key in keys.get(
        dataset_type,
        [],
    ):
        column = find_column(
            df,
            [key],
        )

        if column is not None:
            selected_keys.append(column)

    if not selected_keys:
        return df

    key_frame = df[selected_keys].copy()

    has_value = key_frame.notna().any(
        axis=1
    )

    duplicate_mask = (
        key_frame
        .astype("string")
        .apply(
            lambda column: column.str.strip().str.lower()
        )
        .duplicated(
            keep="first"
        )
    )

    return df[
        ~(duplicate_mask & has_value)
    ].copy()


# Clean one uploaded file.
def clean_uploaded_file(
    file,
    dataset_type,
    options,
):
    if isinstance(file, dict):
        possible_file = (
            file.get("file")
            or file.get("uploaded_file")
            or file.get("data")
        )

        if possible_file is None:
            raise TypeError(
                "Uploaded file is stored as a dictionary "
                "but no file object was found."
            )

        file = possible_file

    if isinstance(file, (bytes, bytearray)):
        file = io.BytesIO(file)

    if hasattr(file, "seek"):
        file.seek(0)

    reader = pd.read_csv(
        file,
        chunksize=CHUNK_SIZE,
        low_memory=False,
    )

    output = io.BytesIO()

    first_chunk = True

    for chunk in reader:
        chunk = chunk.copy()

        if options.get(
            "normalize_missing",
            True,
        ):
            chunk = normalize_missing_values(
                chunk
            )

        if options.get(
            "trim_text",
            True,
        ):
            chunk = trim_text_values(
                chunk
            )

        if dataset_type == "companies":
            chunk = clean_company_data(
                chunk
            )

        elif dataset_type == "startup_funding":
            chunk = clean_startup_data(
                chunk
            )

        elif dataset_type == "state_policies":
            chunk = clean_policy_data(
                chunk
            )

        elif dataset_type == "office_market":
            chunk = clean_office_data(
                chunk
            )

        if options.get(
            "duplicates",
            False,
        ):
            chunk = remove_duplicates(
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


# Generate cleaning options for one dataset.
def generate_cleaning_options(analysis):
    dataset_type = analysis.get(
        "dataset_type",
        "unknown",
    )

    options = []

    missing = analysis.get(
        "missing",
        {},
    )

    missing_total = 0

    for item in missing.values():
        if isinstance(item, dict):
            missing_total += int(
                item.get("count", 0)
            )

    options.append(
        {
            "key": "normalize_missing",
            "label": "Normalize missing values",
            "details": (
                f"{missing_total:,} "
                "missing or blank values detected."
            ),
            "recommended": True,
        }
    )

    options.append(
        {
            "key": "trim_text",
            "label": "Trim text values",
            "details": (
                "Remove unnecessary spaces from text fields."
            ),
            "recommended": True,
        }
    )

    if dataset_type == "companies":
        options.extend(
            [
                {
                    "key": "company_dates",
                    "label": "Normalize registration dates",
                    "details": (
                        "Convert registration dates "
                        "to YYYY-MM-DD."
                    ),
                    "recommended": True,
                },
                {
                    "key": "company_years",
                    "label": "Convert financial years",
                    "details": (
                        "Convert year/date values "
                        "to four-digit years."
                    ),
                    "recommended": True,
                },
                {
                    "key": "industrial_class",
                    "label": "Normalize industrial class",
                    "details": (
                        "Normalize industrial class values."
                    ),
                    "recommended": True,
                },
            ]
        )

    elif dataset_type == "startup_funding":
        options.append(
            {
                "key": "startup_fields",
                "label": "Standardize funding fields",
                "details": (
                    "Prepare sector, stage, amount, "
                    "investor and date fields."
                ),
                "recommended": True,
            }
        )

    elif dataset_type == "state_policies":
        options.append(
            {
                "key": "policy_fields",
                "label": "Prepare policy dates and benefits",
                "details": (
                    "Convert policy periods and "
                    "combine benefit fields."
                ),
                "recommended": True,
            }
        )

    elif dataset_type == "office_market":
        options.append(
            {
                "key": "office_fields",
                "label": "Prepare office market values",
                "details": (
                    "Calculate average rent from "
                    "minimum and maximum values "
                    "and convert market periods."
                ),
                "recommended": True,
            }
        )

    duplicate_info = analysis.get(
        "duplicates",
        {},
    )

    duplicate_count = 0

    if isinstance(
        duplicate_info,
        dict,
    ):
        duplicate_count = int(
            duplicate_info.get(
                "count",
                0,
            )
        )

    if duplicate_count > 0:
        options.append(
            {
                "key": "duplicates",
                "label": "Remove duplicate records",
                "details": (
                    f"{duplicate_count:,} "
                    "duplicate rows detected."
                ),
                "recommended": True,
            }
        )

    return options


# Find uploaded files regardless of list or dictionary storage.
def build_uploaded_lookup(uploaded_files):
    lookup = {}

    if uploaded_files is None:
        return lookup

    if isinstance(
        uploaded_files,
        dict,
    ):
        items = uploaded_files.items()

        for name, value in items:
            if hasattr(value, "seek"):
                lookup[str(name)] = value
                continue

            if isinstance(value, dict):
                candidate = (
                    value.get("file")
                    or value.get("uploaded_file")
                    or value.get("data")
                )

                if candidate is not None:
                    lookup[str(name)] = candidate

        return lookup

    for item in uploaded_files:
        if hasattr(item, "name"):
            lookup[str(item.name)] = item

        elif isinstance(item, dict):
            name = (
                item.get("name")
                or item.get("file_name")
                or item.get("filename")
            )

            candidate = (
                item.get("file")
                or item.get("uploaded_file")
                or item.get("data")
            )

            if (
                name is not None
                and candidate is not None
            ):
                lookup[str(name)] = candidate

    return lookup


# Save a cleaned CSV with a timestamp.
def save_cleaned_csv(
    cleaned_file,
    original_file_name,
):
    base_dir = Path(__file__).resolve().parents[1]

    cleaned_dir = (
        base_dir
        / "data"
        / "cleaned"
    )

    cleaned_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    original_name = Path(
        original_file_name
    ).stem

    output_name = (
        f"{original_name}"
        f"_cleaned_{timestamp}.csv"
    )

    output_path = (
        cleaned_dir
        / output_name
    )

    cleaned_file.seek(0)

    with output_path.open(
        "wb"
    ) as destination:
        destination.write(
            cleaned_file.read()
        )

    cleaned_file.seek(0)

    return output_path


# Count rows in a cleaned CSV.
def count_file_rows(file):
    if isinstance(file, dict):
        file = (
            file.get("file")
            or file.get("uploaded_file")
            or file.get("data")
        )

    if isinstance(
        file,
        (bytes, bytearray),
    ):
        file = io.BytesIO(file)

    file.seek(0)

    rows = 0

    for chunk in pd.read_csv(
        file,
        chunksize=CHUNK_SIZE,
        low_memory=False,
    ):
        rows += len(chunk)

    file.seek(0)

    return rows


# Clean all datasets.
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

    uploaded_lookup = build_uploaded_lookup(
        uploaded_files
    )

    cleaned_files = {}
    cleaned_file_metadata = {}
    results = {}

    for file_name, analysis in analyses.items():
        original_file = uploaded_lookup.get(
            file_name
        )

        if original_file is None:
            results[file_name] = {
                "status": "failed",
                "rows": 0,
                "error": (
                    "Original uploaded file "
                    "could not be found."
                ),
            }

            continue

        try:
            dataset_type = analysis.get(
                "dataset_type",
                "unknown",
            )

            options = cleaning_options.get(
                file_name,
                {},
            )

            if not isinstance(
                options,
                dict,
            ):
                options = {}

            cleaned_file = clean_uploaded_file(
                original_file,
                dataset_type,
                options,
            )

            row_count = count_file_rows(
                cleaned_file
            )

            output_path = save_cleaned_csv(
                cleaned_file,
                file_name,
            )

            cleaned_file.seek(0)

            cleaned_files[file_name] = (
                cleaned_file
            )

            cleaned_file_metadata[
                file_name
            ] = {
                "source_file": file_name,
                "cleaned_file": output_path.name,
                "path": str(output_path),
                "rows": row_count,
                "dataset_type": dataset_type,
            }

            results[file_name] = {
                "status": "success",
                "rows": row_count,
                "path": str(output_path),
                "cleaned_file": output_path.name,
            }

        except Exception as error:
            results[file_name] = {
                "status": "failed",
                "rows": 0,
                "error": (
                    f"{type(error).__name__}: "
                    f"{str(error)}"
                ),
            }

    st.session_state.cleaned_files = (
        cleaned_files
    )

    st.session_state.cleaned_file_metadata = (
        cleaned_file_metadata
    )

    st.session_state.cleaning_results = (
        results
    )

    return results


# Render the cleaning stage.
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

        option_list = (
            generate_cleaning_options(
                analysis
            )
        )

        selected = {}

        for option in option_list:
            key = option.get(
                "key"
            )

            label = option.get(
                "label",
                key,
            )

            details = option.get(
                "details",
                "",
            )

            selected[key] = st.checkbox(
                label,
                value=bool(
                    option.get(
                        "recommended",
                        True,
                    )
                ),
                key=(
                    f"clean_"
                    f"{file_name}_"
                    f"{key}"
                ),
            )

            if details:
                st.caption(
                    details
                )

        all_cleaning_options[
            file_name
        ] = selected

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
            with st.spinner(
                "Cleaning datasets..."
            ):
                results = clean_all_datasets(
                    analyses,
                    all_cleaning_options,
                    uploaded_files,
                )

            failed = {
                name: result
                for name, result in results.items()
                if result.get("status") != "success"
            }

            successful = {
                name: result
                for name, result in results.items()
                if result.get("status") == "success"
            }

            if successful:
                st.success(
                    f"{len(successful)} "
                    "dataset(s) cleaned successfully."
                )

            if failed:
                st.error(
                    f"{len(failed)} "
                    "dataset(s) failed to clean."
                )

                for file_name, result in failed.items():
                    st.error(
                        f"{file_name}: "
                        f"{result.get('error', 'Unknown error')}"
                    )

            if not failed:
                st.session_state.cleaning_done = (
                    True
                )

                st.session_state.upload_stage = (
                    4
                )

                st.rerun()