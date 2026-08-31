import pandas as pd


CHUNK_SIZE = 50000


# Detect the target dataset from the uploaded filename.
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


# Calculate a percentage safely.
def percentage(value, total):
    if total == 0:
        return 0.0

    return round(
        (value / total) * 100,
        2
    )


# Analyse missing and empty values using CSV chunks.
def analyse_missing_values(file):
    file.seek(0)

    total_rows = 0
    missing_counts = None
    empty_counts = None
    columns = []

    for chunk in pd.read_csv(
        file,
        chunksize=CHUNK_SIZE,
        low_memory=False
    ):
        if not columns:
            columns = list(chunk.columns)

            missing_counts = pd.Series(
                0,
                index=columns,
                dtype="int64"
            )

            empty_counts = pd.Series(
                0,
                index=columns,
                dtype="int64"
            )

        total_rows += len(chunk)

        missing_counts = (
            missing_counts
            .add(
                chunk.isna().sum(),
                fill_value=0
            )
            .astype("int64")
        )

        empty_counts = (
            empty_counts
            .add(
                chunk.astype("string")
                .apply(
                    lambda column: column.str.strip().eq("").sum()
                )
            )
            .astype("int64")
        )

    file.seek(0)

    quality_rows = []

    if missing_counts is not None:

        for column in columns:

            missing = int(
                missing_counts[column]
            )

            empty = int(
                empty_counts[column]
            )

            total_issue = missing + empty

            quality_rows.append(
                {
                    "Column": column,
                    "Missing": missing,
                    "Missing %": percentage(
                        missing,
                        total_rows
                    ),
                    "Empty": empty,
                    "Empty %": percentage(
                        empty,
                        total_rows
                    ),
                    "Total issues": total_issue,
                    "Issue %": percentage(
                        total_issue,
                        total_rows
                    )
                }
            )

    return (
        total_rows,
        columns,
        quality_rows
    )


# Analyse date columns.
def analyse_date_columns(file, dataset_type):
    file.seek(0)

    candidates = {
        "companies": [
            "DATE_OF_REGISTRATION"
        ],
        "startup_funding": [
            "funding_date",
            "FUNDING_DATE"
        ],
        "office_market": [
            "market_date",
            "MARKET_DATE",
            "data_period"
        ],
        "state_policies": [
            "effective_from",
            "effective_to",
            "policy_period"
        ]
    }

    columns_to_check = candidates.get(
        dataset_type,
        []
    )

    invalid = {}
    totals = {}

    for chunk in pd.read_csv(
        file,
        chunksize=CHUNK_SIZE,
        low_memory=False
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
                    r"^\d{4}(-\d{4})?$"
                )

            elif column == "data_period":

                valid_mask = values.str.match(
                    r"^(Q[1-4]\s+)?\d{4}$"
                )

            else:

                valid_mask = (
                    pd.to_datetime(
                        values,
                        errors="coerce"
                    ).notna()
                )

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
                totals.get(column, 0)
            )
        }

    return result


# Analyse numeric columns.
def analyse_numeric_columns(file, dataset_type):
    file.seek(0)

    candidates = {
        "companies": [
            "AUTHORIZED_CAP",
            "PAIDUP_CAPITAL",
            "INDUSTRIAL_CLASS",
            "LATEST_YEAR_ANNUAL_RETURN",
            "LATEST_YEAR_FINANCIAL_STATEMENT"
        ],
        "startup_funding": [
            "funding_amount",
            "amount_usd_numeric"
        ],
        "office_market": [
            "rent_per_sqft",
            "rent_per_sqm",
            "rent_min_inr_per_sqft_month",
            "rent_max_inr_per_sqft_month",
            "vacancy_rate"
        ]
    }

    columns_to_check = candidates.get(
        dataset_type,
        []
    )

    invalid = {}
    totals = {}

    for chunk in pd.read_csv(
        file,
        chunksize=CHUNK_SIZE,
        low_memory=False
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

            valid = pd.to_numeric(
                values.str.replace(
                    ",",
                    "",
                    regex=False
                ),
                errors="coerce"
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
                totals.get(column, 0)
            )
        }

    return result


# Analyse duplicate business keys without loading the complete file.
def analyse_duplicates(file, dataset_type):
    file.seek(0)

    key_columns = {
        "companies": [
            "CORPORATE_IDENTIFICATION_NUMBER"
        ],
        "startup_funding": [
            "startup_name",
            "funding_date",
            "funding_amount",
            "city"
        ],
        "state_policies": [
            "state",
            "policy_name",
            "sector"
        ],
        "office_market": [
            "city",
            "state",
            "locality",
            "property_type",
            "market_date"
        ]
    }

    keys = key_columns.get(
        dataset_type,
        []
    )

    if not keys:
        file.seek(0)

        return {
            "count": 0,
            "percentage": 0
        }

    seen = set()
    duplicate_count = 0
    total_rows = 0

    for chunk in pd.read_csv(
        file,
        chunksize=CHUNK_SIZE,
        low_memory=False
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
            name=None
        ):

            total_rows += 1

            normalized = tuple(
                None
                if pd.isna(value)
                else str(value).strip().lower()
                for value in values
            )

            if normalized in seen:
                duplicate_count += 1
            else:
                seen.add(normalized)

    file.seek(0)

    return {
        "count": duplicate_count,
        "percentage": percentage(
            duplicate_count,
            total_rows
        )
    }


# Analyse one uploaded dataset.
def analyse_uploaded_file(file):
    try:

        dataset_type = detect_dataset_type(
            file.name
        )

        (
            total_rows,
            columns,
            quality_report
        ) = analyse_missing_values(
            file
        )

        date_issues = analyse_date_columns(
            file,
            dataset_type
        )

        numeric_issues = analyse_numeric_columns(
            file,
            dataset_type
        )

        duplicates = analyse_duplicates(
            file,
            dataset_type
        )

        return {
            "status": "success",
            "dataset_type": dataset_type,
            "file_name": file.name,
            "row_count": total_rows,
            "column_count": len(columns),
            "rows": total_rows,
            "columns": columns,
            "quality_report": pd.DataFrame(
                quality_report
            ),
            "missing": {
                row["Column"]: {
                    "count": row["Missing"],
                    "percentage": row["Missing %"]
                }
                for row in quality_report
            },
            "date_issues": date_issues,
            "numeric_issues": numeric_issues,
            "duplicates": duplicates
        }

    except Exception as error:

        return {
            "status": "failed",
            "file_name": file.name,
            "error": str(error),
            "row_count": 0,
            "column_count": 0,
            "rows": 0,
            "columns": []
        }


# Return the summary required by the analysis dashboard.
def get_quality_summary(analysis):

    quality_report = analysis.get(
        "quality_report",
        pd.DataFrame()
    )

    columns_with_nulls = 0
    columns_with_empty_values = 0

    if not quality_report.empty:

        columns_with_nulls = int(
            (
                quality_report["Missing"] > 0
            ).sum()
        )

        columns_with_empty_values = int(
            (
                quality_report["Empty"] > 0
            ).sum()
        )

    duplicates = analysis.get(
        "duplicates",
        {}
    )

    return {
        "rows": analysis.get(
            "row_count",
            0
        ),
        "columns": analysis.get(
            "column_count",
            0
        ),
        "duplicate_rows": duplicates.get(
            "count",
            0
        ),
        "columns_with_nulls": columns_with_nulls,
        "columns_with_empty_values": columns_with_empty_values
    }