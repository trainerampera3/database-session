from pathlib import Path
import psycopg
import pandas as pd
import io


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def create_connection():
    try:
        connection = psycopg.connect(
            host="localhost",
            dbname="postgres",
            user="gajapathi",
            password="admin@123"
        )

        print("Connection successful.")
        return connection

    except Exception as e:
        print(f"Connection error: {e}")
        return None


def load_dimension_table(connection, csv_file, table_name):

    file_path = DATA_DIR / csv_file

    print(f"\nLoading {csv_file}...")

    df = pd.read_csv(
        file_path,
        encoding="latin1"
    )

    # Special handling for time_dim
    if table_name == "time_dim":
        df["date"] = pd.to_datetime(
            df["date"],
            format="%d-%m-%Y %H:%M"
        )

    # Convert NaN to None
    df = df.where(pd.notna(df), None)

    columns = list(df.columns)

    column_names = ", ".join(
        f'"{column}"' for column in columns
    )

    placeholders = ", ".join(
        ["%s"] * len(columns)
    )

    query = f"""
        INSERT INTO {table_name} ({column_names})
        VALUES ({placeholders})
    """

    with connection.cursor() as cursor:

        cursor.executemany(
            query,
            df.itertuples(
                index=False,
                name=None
            )
        )

    connection.commit()

    print(f"{len(df)} rows inserted into {table_name}.")


def load_fact_table(connection):
    file_path = DATA_DIR / "fact_table.csv"

    print("\nLoading fact_table.csv...")
    print("This contains 1,000,000 rows, so COPY will be used.")

    df = pd.read_csv(
        file_path,
        encoding="latin1"
    )

    # Convert NaN to PostgreSQL NULL
    df = df.where(pd.notna(df), None)

    buffer = io.StringIO()

    df.to_csv(
        buffer,
        index=False,
        header=False
    )

    buffer.seek(0)

    columns = [
        "payment_key",
        "coustomer_key",
        "time_key",
        "item_key",
        "store_key",
        "quantity",
        "unit",
        "unit_price",
        "total_price"
    ]

    column_names = ", ".join(columns)

    with connection.cursor() as cursor:

        with cursor.copy(
            f"""
            COPY fact_table ({column_names})
            FROM STDIN
            WITH (FORMAT CSV)
            """
        ) as copy:

            copy.write(buffer.getvalue())

    connection.commit()

    print("1,000,000 fact rows inserted successfully.")


def main():

    connection = create_connection()

    if not connection:
        return

    try:

        # Load dimensions FIRST
        load_dimension_table(
            connection,
            "Trans_dim.csv",
            "trans_dim"
        )

        load_dimension_table(
            connection,
            "customer_dim.csv",
            "customer_dim"
        )

        load_dimension_table(
            connection,
            "item_dim.csv",
            "item_dim"
        )

        load_dimension_table(
            connection,
            "store_dim.csv",
            "store_dim"
        )

        load_dimension_table(
            connection,
            "time_dim.csv",
            "time_dim"
        )

        # Fact table LAST
        load_fact_table(connection)

        print("\nAll data loaded successfully!")

    except Exception as e:

        connection.rollback()

        print(f"\nError while loading data: {e}")

    finally:

        connection.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()