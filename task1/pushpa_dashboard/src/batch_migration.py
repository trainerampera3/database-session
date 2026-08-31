import pandas as pd
from datetime import datetime

from db import get_connection
from migration_report import create_report
from batch_log import (
    start_batch,
    complete_batch,
    fail_batch
)


BATCH_SIZE = 1000


def migrate_data():

    start_time = datetime.now()

    train_info = pd.read_csv(
        "src/Data/processed/train_info_cleaned.csv"
    )

    train_schedule = pd.read_csv(
        "src/Data/processed/train_schedule_cleaned.csv"
    )

    batch_id = start_batch(2)

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            for start in range(
                0,
                len(train_info),
                BATCH_SIZE
            ):

                batch = train_info.iloc[
                    start:start + BATCH_SIZE
                ]

                for row in batch.itertuples(
                    index=False,
                    name=None
                ):

                    values = tuple(
                        None
                        if pd.isna(value)
                        else value.item()
                        if hasattr(value, "item")
                        else value
                        for value in row
                    )

                    cur.execute(
                        """
                        SELECT insert_train_info(
                            %s::INTEGER,
                            %s::TEXT,
                            %s::TEXT,
                            %s::TEXT,
                            %s::TEXT
                        )
                        """,
                        values
                    )


            for start in range(
                0,
                len(train_schedule),
                BATCH_SIZE
            ):

                batch = train_schedule.iloc[
                    start:start + BATCH_SIZE
                ]

                for row in batch.itertuples(
                    index=False,
                    name=None
                ):

                    values = tuple(
                        None
                        if pd.isna(value)
                        else value.item()
                        if hasattr(value, "item")
                        else value
                        for value in row
                    )

                    cur.execute(
                        """
                        SELECT insert_train_schedule(
                            %s::INTEGER,
                            %s::INTEGER,
                            %s::TEXT,
                            %s::INTEGER,
                            %s::INTEGER,
                            %s::INTEGER,
                            %s::INTEGER,
                            %s::TEXT,
                            %s::INTEGER,
                            %s::TIME,
                            %s::TIME,
                            %s::DOUBLE PRECISION
                        )
                        """,
                        values
                    )

        conn.commit()

        end_time = datetime.now()

        total_rows = (
            len(train_info)
            + len(train_schedule)
        )

        complete_batch(
            batch_id,
            total_rows
        )

        report = create_report(
            len(train_info),
            len(train_schedule),
            start_time,
            end_time
        )

        return report

    except Exception as error:

        conn.rollback()

        fail_batch(
            batch_id,
            str(error)
        )

        raise

    finally:

        conn.close()


if __name__ == "__main__":

    report = migrate_data()

    print()
    print("Migration Report")
    print("----------------")
    print("Status:", report["status"])
    print("Files:", report["files"])
    print(
        "Train Info Rows:",
        report["train_info_rows"]
    )
    print(
        "Train Schedule Rows:",
        report["train_schedule_rows"]
    )
    print(
        "Total Rows:",
        report["total_rows"]
    )
    print(
        "Duration:",
        report["duration"]
    )
    print(
        "Result:",
        report["result"]
    )