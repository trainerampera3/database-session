import json
from datetime import datetime
import pandas as pd
import psycopg
from database.load import ensure_procedure, ensure_schema
from processing.cleaning import clean_dataset
from processing.transform import transform_dataset
from processing.validate import validate_dataset


DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "dbname": "job_management",
    "user": "deepika",
    "password": "deepu1014",
}

def generate_run_id(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COALESCE(
                MAX(
                    CAST(
                        REPLACE(run_id::text, 'RUN-', '')
                        AS INTEGER
                    )
                ),
                0
            ) + 1
            FROM batch_log
            WHERE run_id::text LIKE 'RUN-%';
            """
        )
        next_number = cursor.fetchone()[0]

    return f"RUN-{next_number:03d}"

 
def save_pipeline_log(
    connection,
    run_id,
    pipeline_started,
    completed,
    status,
    records,
    error=None
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO batch_log (
                run_id,
                pipeline_started,
                completed,
                status,
                records,
                error
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            );
            """,
            (
                run_id,
                pipeline_started,
                completed,
                status,
                records,
                error
            )
        )

    connection.commit()

def process_batches(
    raw_df,
    column_mapping,
    batch_size=100
):
    total_records = len(raw_df)

    if total_records == 0:
        raise ValueError(
            "Raw dataset contains no records."
        )
    if batch_size <= 0:
        raise ValueError(
            "Batch size must be greater than 0."
        )
    total_batches = (
        (
            total_records
            + batch_size
            - 1
        )
        // batch_size
    )
    logs = []
    pipeline_started = datetime.now()

    print("=" * 70)
    print("RAW DATA BATCH PROCESSING")
    print("=" * 70)

    print(
        f"Total records: {total_records}"
    )
    print(
        f"Batch size: {batch_size}"
    )
    print(
        f"Total batches: {total_batches}"
    )
    with psycopg.connect(
        **DB_CONFIG
    ) as connection:

        ensure_schema(connection)
        ensure_procedure(connection)
        run_id = generate_run_id(connection)

        try:
            with connection.cursor() as cursor:

                for batch_number, start in enumerate(
                    range(
                        0,
                        total_records,
                        batch_size
                    ),
                    start=1
                ):

                    end = min(
                        start + batch_size,
                        total_records
                    )
                    print()
                    print(
                        "=" * 70
                    )
                    print(
                        f"BATCH "
                        f"{batch_number}/{total_batches}"
                    )
                    print(
                        f"Raw records "
                        f"{start + 1}-{end}"
                    )
                    print(
                        "=" * 70
                    )
                    batch = raw_df.iloc[
                        start:end
                    ].copy()
                    print(
                        f"Raw records: "
                        f"{len(batch)}"
                    )
                    print(
                        "Step 1/5: Cleaning..."
                    )
                    cleaned_batch = clean_dataset(
                        batch
                    )
                    print(
                        "Cleaning completed."
                    )
                    print(
                        "Step 2/5: Mapping + Transforming..."
                    )
                    transformed_batch = transform_dataset(
                        cleaned_batch,
                        column_mapping
                    )
                    print(
                        "Mapping + transformation completed."
                    )
                    print(
                        "Step 3/5: Validating..."
                    )
                    validation_result = validate_dataset(
                        transformed_batch
                    )
                    if not validation_result["valid"]:

                        error_count = (
                            validation_result[
                                "error_count"
                            ]
                        )

                        print(
                            f"Validation FAILED "
                            f"with {error_count} errors."
                        )

                        logs.append({
                            "batch": batch_number,
                            "records": len(batch),
                            "status": "FAILED",
                            "stage": "Validation",
                            "error_count": error_count,
                            "errors": validation_result[
                                "errors"
                            ]
                        })

                        continue

                    print(
                        "Validation successful."
                    )
                    print(
                        "Step 4/5: Calling stored procedure..."
                    )
                    batch_records = (
                        transformed_batch
                        .to_dict(
                            orient="records"
                        )
                    )
                    batch_json = json.dumps(
                        batch_records,
                        default=str
                    )
                    cursor.execute(
                        "CALL process_job_batch(%s::jsonb)",
                        (batch_json,)
                    )
                    print(
                        "Stored procedure completed."
                    )
                    connection.commit()
                    print(
                        f"Batch {batch_number} "
                        f"stored successfully."
                    )
                    logs.append({
                        "batch": batch_number,
                        "records": len(batch),
                        "status": "SUCCESS",
                        "stage": "Stored Procedure",
                        "error_count": 0,
                        "errors": []
                    })

            successful_batches = sum(
                1
                for log in logs
                if log["status"] == "SUCCESS"
            )
            failed_batches = sum(
                1
                for log in logs
                if log["status"] == "FAILED"
            )
            completed = datetime.now()
            records_processed = sum(
                log.get("records", 0)
                for log in logs
                if log["status"] == "SUCCESS"
            )
            print()
            print("=" * 70)
            print("BATCH PROCESSING COMPLETED")
            print("=" * 70)

            print(
                f"Total batches: "
                f"{total_batches}"
            )
            print(
                f"Successful batches: "
                f"{successful_batches}"
            )
            print(
                f"Failed batches: "
                f"{failed_batches}"
            )
            print("=" * 70)
            print("Saving pipeline log to PostgreSQL...")
            save_pipeline_log(
                connection,
                run_id,
                pipeline_started,                                                           
                completed,                                                                    
                "SUCCESS",
                records_processed,
                None,
            )
            print("Pipeline log saved successfully.")

            return logs
        except Exception as exc:
            completed = datetime.now()
            print(f"Pipeline failed: {exc}")
            save_pipeline_log(
                connection,
                run_id,
                pipeline_started,
                completed,
                "FAILED",
                0,
                str(exc),
            )
            raise

if __name__ == "__main__":

    print(
        "run_pipeline.py loaded successfully."
    )