import json
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd

BATCH_SIZE = 5000

PROCEDURES = {
    "companies": "business_location.insert_companies_batch",
    "startup_funding": "business_location.insert_startup_funding_batch",
    "state_policies": "business_location.insert_state_policies_batch",
    "office_market": "business_location.insert_office_market_batch",
}

# Create stored procedures for all target tables.
def create_stored_procedures(connection):
    procedures = [
        """
        CREATE OR REPLACE PROCEDURE business_location.insert_companies_batch(
            p_rows JSONB,
            INOUT p_inserted INTEGER,
            INOUT p_rejected INTEGER,
            INOUT p_invalid INTEGER,
            INOUT p_error TEXT
        )
        LANGUAGE plpgsql
        AS $proc$
        DECLARE
            item JSONB;
            affected_rows INTEGER;
            error_text TEXT;
        BEGIN
            p_inserted := 0;
            p_rejected := 0;
            p_invalid := 0;
            p_error := NULL;

            FOR item IN SELECT value FROM jsonb_array_elements(p_rows)
            LOOP
                BEGIN
                    INSERT INTO business_location.companies (
                        corporate_identification_number,
                        company_name,
                        company_status,
                        company_class,
                        company_category,
                        company_sub_category,
                        registration_date,
                        registered_state,
                        authorized_cap,
                        paidup_capital,
                        industrial_class,
                        business_activity,
                        registered_office_address,
                        registrar_of_companies,
                        email_addr,
                        latest_year_annual_return,
                        latest_year_financial_statement
                    )
                    VALUES (
                        NULLIF(item->>'corporate_identification_number', ''),
                        NULLIF(item->>'company_name', ''),
                        NULLIF(item->>'company_status', ''),
                        NULLIF(item->>'company_class', ''),
                        NULLIF(item->>'company_category', ''),
                        NULLIF(item->>'company_sub_category', ''),
                        CASE
                            WHEN NULLIF(item->>'registration_date', '') IS NULL THEN NULL
                            WHEN item->>'registration_date' ~ '^\\d{4}-\\d{2}-\\d{2}$'
                                THEN (item->>'registration_date')::DATE
                            WHEN item->>'registration_date' ~ '^\\d{2}-\\d{2}-\\d{4}$'
                                THEN to_date(item->>'registration_date', 'DD-MM-YYYY')
                            ELSE NULL
                        END,
                        NULLIF(item->>'registered_state', ''),
                        NULLIF(item->>'authorized_cap', '')::NUMERIC,
                        NULLIF(item->>'paidup_capital', '')::NUMERIC,
                        NULLIF(item->>'industrial_class', ''),
                        NULLIF(item->>'business_activity', ''),
                        NULLIF(item->>'registered_office_address', ''),
                        NULLIF(item->>'registrar_of_companies', ''),
                        NULLIF(item->>'email_addr', ''),
                        CASE
                            WHEN item->>'latest_year_annual_return' ~ '^\\d{4}$'
                                THEN (item->>'latest_year_annual_return')::INTEGER
                            ELSE NULL
                        END,
                        CASE
                            WHEN item->>'latest_year_financial_statement' ~ '^\\d{4}$'
                                THEN (item->>'latest_year_financial_statement')::INTEGER
                            ELSE NULL
                        END
                    )
                    ON CONFLICT DO NOTHING;

                    GET DIAGNOSTICS affected_rows = ROW_COUNT;

                    IF affected_rows = 1 THEN
                        p_inserted := p_inserted + 1;
                    ELSE
                        p_rejected := p_rejected + 1;
                    END IF;
                EXCEPTION WHEN OTHERS THEN
                    p_rejected := p_rejected + 1;
                    p_invalid := p_invalid + 1;
                    GET STACKED DIAGNOSTICS error_text = MESSAGE_TEXT;
                    IF p_error IS NULL THEN
                        p_error := error_text;
                    END IF;
                END;
            END LOOP;
        END;
        $proc$;
        """,
        """
        CREATE OR REPLACE PROCEDURE business_location.insert_startup_funding_batch(
            p_rows JSONB,
            INOUT p_inserted INTEGER,
            INOUT p_rejected INTEGER,
            INOUT p_invalid INTEGER,
            INOUT p_error TEXT
        )
        LANGUAGE plpgsql
        AS $proc$
        DECLARE
            item JSONB;
            affected_rows INTEGER;
            error_text TEXT;
        BEGIN
            p_inserted := 0;
            p_rejected := 0;
            p_invalid := 0;
            p_error := NULL;

            FOR item IN SELECT value FROM jsonb_array_elements(p_rows)
            LOOP
                BEGIN
                    INSERT INTO business_location.startup_funding (
                        startup_name, city, state, sector, funding_stage,
                        funding_amount, funding_date, investor_name, source
                    )
                    VALUES (
                        NULLIF(item->>'startup_name', ''),
                        NULLIF(item->>'city', ''),
                        NULLIF(item->>'state', ''),
                        NULLIF(item->>'sector', ''),
                        NULLIF(item->>'funding_stage', ''),
                        NULLIF(item->>'funding_amount', '')::NUMERIC,
                        CASE
                            WHEN NULLIF(item->>'funding_date', '') IS NULL THEN NULL
                            WHEN item->>'funding_date' ~ '^\\d{4}-\\d{2}-\\d{2}$'
                                THEN (item->>'funding_date')::DATE
                            WHEN item->>'funding_date' ~ '^\\d{2}-\\d{2}-\\d{4}$'
                                THEN to_date(item->>'funding_date', 'DD-MM-YYYY')
                            ELSE NULL
                        END,
                        NULLIF(item->>'investor_name', ''),
                        NULLIF(item->>'source', '')
                    )
                    ON CONFLICT DO NOTHING;

                    GET DIAGNOSTICS affected_rows = ROW_COUNT;
                    IF affected_rows = 1 THEN
                        p_inserted := p_inserted + 1;
                    ELSE
                        p_rejected := p_rejected + 1;
                    END IF;
                EXCEPTION WHEN OTHERS THEN
                    p_rejected := p_rejected + 1;
                    p_invalid := p_invalid + 1;
                    GET STACKED DIAGNOSTICS error_text = MESSAGE_TEXT;
                    IF p_error IS NULL THEN
                        p_error := error_text;
                    END IF;
                END;
            END LOOP;
        END;
        $proc$;
        """,
        """
        CREATE OR REPLACE PROCEDURE business_location.insert_state_policies_batch(
            p_rows JSONB,
            INOUT p_inserted INTEGER,
            INOUT p_rejected INTEGER,
            INOUT p_invalid INTEGER,
            INOUT p_error TEXT
        )
        LANGUAGE plpgsql
        AS $proc$
        DECLARE
            item JSONB;
            affected_rows INTEGER;
            error_text TEXT;
        BEGIN
            p_inserted := 0;
            p_rejected := 0;
            p_invalid := 0;
            p_error := NULL;

            FOR item IN SELECT value FROM jsonb_array_elements(p_rows)
            LOOP
                BEGIN
                    INSERT INTO business_location.state_policies (
                        state, policy_name, sector, incentive_type,
                        incentive_description, eligibility, benefit,
                        effective_from, effective_to, source
                    )
                    VALUES (
                        NULLIF(item->>'state', ''),
                        NULLIF(item->>'policy_name', ''),
                        NULLIF(item->>'sector', ''),
                        NULLIF(item->>'incentive_type', ''),
                        NULLIF(item->>'incentive_description', ''),
                        NULLIF(item->>'eligibility', ''),
                        NULLIF(item->>'benefit', ''),
                        CASE
                            WHEN NULLIF(item->>'effective_from', '') IS NULL THEN NULL
                            WHEN item->>'effective_from' ~ '^\\d{4}-\\d{2}-\\d{2}$'
                                THEN (item->>'effective_from')::DATE
                            ELSE NULL
                        END,
                        CASE
                            WHEN NULLIF(item->>'effective_to', '') IS NULL THEN NULL
                            WHEN item->>'effective_to' ~ '^\\d{4}-\\d{2}-\\d{2}$'
                                THEN (item->>'effective_to')::DATE
                            ELSE NULL
                        END,
                        NULLIF(item->>'source', '')
                    )
                    ON CONFLICT DO NOTHING;

                    GET DIAGNOSTICS affected_rows = ROW_COUNT;
                    IF affected_rows = 1 THEN
                        p_inserted := p_inserted + 1;
                    ELSE
                        p_rejected := p_rejected + 1;
                    END IF;
                EXCEPTION WHEN OTHERS THEN
                    p_rejected := p_rejected + 1;
                    p_invalid := p_invalid + 1;
                    GET STACKED DIAGNOSTICS error_text = MESSAGE_TEXT;
                    IF p_error IS NULL THEN
                        p_error := error_text;
                    END IF;
                END;
            END LOOP;
        END;
        $proc$;
        """,
        """
        CREATE OR REPLACE PROCEDURE business_location.insert_office_market_batch(
            p_rows JSONB,
            INOUT p_inserted INTEGER,
            INOUT p_rejected INTEGER,
            INOUT p_invalid INTEGER,
            INOUT p_error TEXT
        )
        LANGUAGE plpgsql
        AS $proc$
        DECLARE
            item JSONB;
            affected_rows INTEGER;
            error_text TEXT;
        BEGIN
            p_inserted := 0;
            p_rejected := 0;
            p_invalid := 0;
            p_error := NULL;

            FOR item IN SELECT value FROM jsonb_array_elements(p_rows)
            LOOP
                BEGIN
                    INSERT INTO business_location.office_market (
                        city, state, locality, property_type,
                        rent_per_sqft, rent_per_sqm, vacancy_rate,
                        availability, market_date, source
                    )
                    VALUES (
                        NULLIF(item->>'city', ''),
                        NULLIF(item->>'state', ''),
                        NULLIF(item->>'locality', ''),
                        NULLIF(item->>'property_type', ''),
                        NULLIF(item->>'rent_per_sqft', '')::NUMERIC,
                        NULLIF(item->>'rent_per_sqm', '')::NUMERIC,
                        NULLIF(item->>'vacancy_rate', '')::NUMERIC,
                        NULLIF(item->>'availability', ''),
                        CASE
                            WHEN NULLIF(item->>'market_date', '') IS NULL THEN NULL
                            WHEN item->>'market_date' ~ '^\\d{4}-\\d{2}-\\d{2}$'
                                THEN (item->>'market_date')::DATE
                            WHEN item->>'market_date' ~ '^\\d{2}-\\d{2}-\\d{4}$'
                                THEN to_date(item->>'market_date', 'DD-MM-YYYY')
                            ELSE NULL
                        END,
                        NULLIF(item->>'source', '')
                    )
                    ON CONFLICT DO NOTHING;

                    GET DIAGNOSTICS affected_rows = ROW_COUNT;
                    IF affected_rows = 1 THEN
                        p_inserted := p_inserted + 1;
                    ELSE
                        p_rejected := p_rejected + 1;
                    END IF;
                EXCEPTION WHEN OTHERS THEN
                    p_rejected := p_rejected + 1;
                    p_invalid := p_invalid + 1;
                    GET STACKED DIAGNOSTICS error_text = MESSAGE_TEXT;
                    IF p_error IS NULL THEN
                        p_error := error_text;
                    END IF;
                END;
            END LOOP;
        END;
        $proc$;
        """,
    ]

    with connection.cursor() as cursor:
        for procedure in procedures:
            cursor.execute(procedure)
    connection.commit()

# Return the procedure name.
def get_procedure(table):
    if table not in PROCEDURES:
        raise ValueError(f"Unsupported target table: {table}")
    return PROCEDURES[table]

# Convert a value to a JSON-safe string.
def safe_value(value):
    if pd.isna(value):
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value).strip()

# Convert a cleaned dataframe to target-column records.
def dataframe_to_records(dataframe, mapping):
    reverse_mapping = {}
    for source, target in mapping.items():
        if target == "Do not map":
            continue
        if source not in dataframe.columns:
            continue
        if target in reverse_mapping:
            raise ValueError(
                f"Target column '{target}' is mapped more than once."
            )
        reverse_mapping[target] = source

    records = []
    for _, row in dataframe.iterrows():
        record = {}
        for target, source in reverse_mapping.items():
            record[target] = safe_value(row[source])
        records.append(record)
    return records

# Insert one batch through the stored procedure.
def insert_batch(connection, table, records):
    payload = json.dumps(records, ensure_ascii=False)

    with connection.cursor() as cursor:
        cursor.execute(
            f"CALL {get_procedure(table)}(%s::JSONB, %s, %s, %s, %s)",
            (payload, 0, 0, 0, ""),
        )
        result = cursor.fetchone()

    connection.commit()

    if result is None:
        raise RuntimeError("Stored procedure returned no batch result.")

    return {
        "inserted": int(result[0] or 0),
        "rejected": int(result[1] or 0),
        "invalid": int(result[2] or 0),
        "error": result[3] or None,
    }

# Write one migration batch to the log.
def write_batch_log(
    connection,
    batch_number,
    source_file,
    target_table,
    rows_processed,
    rows_inserted,
    rows_rejected,
    started_at,
    completed_at,
    status,
    error_message=None,
):
    duration = (completed_at - started_at).total_seconds()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO business_location.batch_log (
                batch_number, source_file, target_table, stage,
                rows_processed, rows_inserted, rows_rejected,
                started_at, completed_at, duration_seconds,
                status, error_message
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                batch_number,
                source_file,
                target_table,
                "Migrate",
                rows_processed,
                rows_inserted,
                rows_rejected,
                started_at,
                completed_at,
                duration,
                status,
                error_message,
            ),
        )
    connection.commit()

# Migrate a cleaned CSV in 5000-row batches.
def migrate_csv_in_batches(
    connection,
    cleaned_file,
    source_file,
    target_table,
    mapping,
    batch_size=BATCH_SIZE,
):
    path = Path(cleaned_file)
    if not path.exists():
        raise FileNotFoundError(f"Cleaned CSV not found: {path}")
    if target_table not in PROCEDURES:
        raise ValueError(f"Unsupported target table: {target_table}")

    total_processed = 0
    total_inserted = 0
    total_rejected = 0
    total_invalid = 0
    batch_count = 0
    last_error = None

    reader = pd.read_csv(
        path,
        chunksize=batch_size,
        low_memory=False,
        dtype=object,
    )

    for dataframe in reader:
        batch_count += 1
        batch_number = f"BAT-{uuid.uuid4().hex[:8].upper()}"
        started_at = datetime.now()
        rows_processed = len(dataframe)
        rows_inserted = 0
        rows_rejected = 0
        invalid_rows = 0
        error_message = None

        try:
            records = dataframe_to_records(dataframe, mapping)
            if not records:
                raise ValueError("Batch contains no rows.")

            result = insert_batch(
                connection,
                target_table,
                records,
            )

            rows_inserted = result["inserted"]
            rows_rejected = result["rejected"]
            invalid_rows = result["invalid"]
            error_message = result["error"]

            if rows_inserted == rows_processed:
                status = "Succeeded"
            elif rows_inserted > 0:
                status = "Partial"
            else:
                status = "Failed"

            if invalid_rows:
                message = f"Invalid rows: {invalid_rows}."
                if error_message:
                    message += f" First error: {error_message}"
                error_message = message
            elif rows_rejected and not error_message:
                error_message = (
                    f"{rows_rejected} rows were not inserted because they "
                    "already existed or violated a database constraint."
                )

        except Exception as error:
            connection.rollback()
            rows_inserted = 0
            rows_rejected = rows_processed
            invalid_rows = rows_processed
            status = "Failed"
            error_message = str(error)

        completed_at = datetime.now()

        write_batch_log(
            connection,
            batch_number,
            source_file,
            target_table,
            rows_processed,
            rows_inserted,
            rows_rejected,
            started_at,
            completed_at,
            status,
            error_message,
        )

        total_processed += rows_processed
        total_inserted += rows_inserted
        total_rejected += rows_rejected
        total_invalid += invalid_rows

        if error_message:
            last_error = error_message

    if total_inserted == total_processed:
        overall_status = "Succeeded"
    elif total_inserted > 0:
        overall_status = "Partial"
    else:
        overall_status = "Failed"

    return {
        "source_file": source_file,
        "target_table": target_table,
        "batches": batch_count,
        "rows_processed": total_processed,
        "rows_inserted": total_inserted,
        "rows_rejected": total_rejected,
        "invalid_rows": total_invalid,
        "status": overall_status,
        "error": last_error,
    }
