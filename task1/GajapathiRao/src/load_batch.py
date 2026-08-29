from pathlib import Path

import pandas as pd
import psycopg

import os
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"



BATCH_SIZES = {
    "trans_dim": 100,
    "customer_dim": 500,
    "item_dim": 100,
    "store_dim": 100,
    "time_dim": 100,
    "fact_table": 10000,
}



TABLE_CONFIG = {

    "trans_dim": {
        "file": "Trans_dim.csv",
        "procedure": "process_trans_batch",
    },

    "customer_dim": {
        "file": "customer_dim.csv",
        "procedure": "process_customer_batch",
    },

    "item_dim": {
        "file": "item_dim.csv",
        "procedure": "process_item_batch",
    },

    "store_dim": {
        "file": "store_dim.csv",
        "procedure": "process_store_batch",
    },

    "time_dim": {
        "file": "time_dim.csv",
        "procedure": "process_time_batch",
    },

    "fact_table": {
        "file": "fact_table.csv",
        "procedure": "process_fact_batch",
    },
}




def create_connection():

    try:

        connection = psycopg.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        print("Database connection successful.")

        return connection

    except Exception as e:

        print(f"Database connection error: {e}")

        return None




def clean_batch(batch, table_name):

   
    if table_name == "time_dim":

        batch["date"] = pd.to_datetime(
            batch["date"],
            format="%d-%m-%Y %H:%M"
        )

    
    batch = batch.where(
        pd.notna(batch),
        None
    )

    return batch



def process_batch(
    connection,
    batch,
    table_name
):

    procedure_name = TABLE_CONFIG[
        table_name
    ]["procedure"]

    batch_json = batch.to_json(
        orient="records",
        date_format="iso"
    )

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                f"""
                CALL {procedure_name}(%s::jsonb)
                """,
                (batch_json,)
            )

        connection.commit()

        return True

    except Exception as e:

        connection.rollback()

        print(
            f"\nBatch failed for {table_name}:"
        )

        print(e)

        return False




def load_table_in_batches(
    connection,
    table_name
):

    config = TABLE_CONFIG[table_name]

    csv_file = config["file"]

    batch_size = BATCH_SIZES[table_name]

    file_path = DATA_DIR / csv_file

    print("\n" + "=" * 60)

    print(f"TABLE      : {table_name}")
    print(f"FILE       : {csv_file}")
    print(f"BATCH SIZE : {batch_size}")
    print(f"PROCEDURE  : {config['procedure']}")

    print("=" * 60)

    batch_number = 0

    total_records = 0

    for batch in pd.read_csv(
        file_path,
        encoding="latin1",
        chunksize=batch_size
    ):

        batch_number += 1

        record_count = len(batch)

        print(
            f"\nProcessing batch {batch_number} "
            f"({record_count} records)"
        )

        # Clean batch
        batch = clean_batch(
            batch,
            table_name
        )

        # Send batch to PostgreSQL
        success = process_batch(
            connection,
            batch,
            table_name
        )

        if not success:

            print(
                f"Stopping {table_name} "
                f"because batch {batch_number} failed."
            )

            raise RuntimeError(
                f"Batch {batch_number} failed "
                f"for {table_name}"
            )

        total_records += record_count

        print(
            f"Batch {batch_number} "
            f"committed successfully."
        )

    print("\n" + "-" * 60)

    print(
        f"{table_name} completed successfully."
    )

    print(
        f"Total batches : {batch_number}"
    )

    print(
        f"Total records : {total_records}"
    )

    print("-" * 60)




def load_all_tables(connection):

    load_order = [
        "trans_dim",
        "customer_dim",
        "item_dim",
        "store_dim",
        "time_dim",
        "fact_table",
    ]

    for table_name in load_order:

        load_table_in_batches(
            connection,
            table_name
        )



def main():

    connection = create_connection()

    if not connection:

        return

    try:

        load_all_tables(connection)

        print(
            "\n"
            + "=" * 60
        )

        print(
            "ALL TABLES LOADED SUCCESSFULLY!"
        )

        print(
            "=" * 60
        )

    except Exception as e:

        print(
            "\nETL PROCESS FAILED."
        )

        print(e)

    finally:

        connection.close()

        print(
            "\nDatabase connection closed."
        )




if __name__ == "__main__":

    main()