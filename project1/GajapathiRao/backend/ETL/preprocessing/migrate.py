import re

import pandas as pd
from psycopg import sql
from psycopg.types.json import Json

from app.database.connection import create_connection


def validate_table_name(table_name: str) -> str:

    if not table_name:

        raise ValueError(
            "Table name is required."
        )

    if not re.match(
        r"^[A-Za-z_][A-Za-z0-9_]*$",
        table_name
    ):

        raise ValueError(
            "Invalid table name. "
            "Use only letters, numbers and underscores."
        )

    return table_name


def get_postgres_type(series: pd.Series) -> str:

    if pd.api.types.is_integer_dtype(series):

        return "BIGINT"

    if pd.api.types.is_float_dtype(series):

        return "DOUBLE PRECISION"

    if pd.api.types.is_bool_dtype(series):

        return "BOOLEAN"

    if pd.api.types.is_datetime64_any_dtype(series):

        return "TIMESTAMP"

    return "TEXT"


def create_table(
    connection,
    df: pd.DataFrame,
    table_name: str,
):

    table_name = validate_table_name(
        table_name
    )

    columns = []

    for column in df.columns:

        column_name = str(column)

        postgres_type = get_postgres_type(
            df[column]
        )

        columns.append(
            sql.SQL("{} {}").format(
                sql.Identifier(column_name),
                sql.SQL(postgres_type)
            )
        )

    query = sql.SQL(
        """
        CREATE TABLE IF NOT EXISTS {} (
            {}
        );
        """
    ).format(
        sql.Identifier(table_name),
        sql.SQL(", ").join(columns)
    )

    with connection.cursor() as cursor:

        cursor.execute(query)

    connection.commit()


def migrate_dataframe(
    df: pd.DataFrame,
    table_name: str,
) -> int:

    if df.empty:

        raise ValueError(
            "Cannot migrate an empty dataset."
        )

    table_name = validate_table_name(
        table_name
    )

    connection = create_connection()

    try:

        create_table(
            connection,
            df,
            table_name
        )

        columns = [
            str(column)
            for column in df.columns
        ]

        column_sql = sql.SQL(", ").join(
            sql.Identifier(column)
            for column in columns
        )

        placeholders = sql.SQL(", ").join(
            sql.Placeholder()
            for _ in columns
        )

        insert_query = sql.SQL(
            """
            INSERT INTO {} ({})
            VALUES ({})
            """
        ).format(
            sql.Identifier(table_name),
            column_sql,
            placeholders
        )

        rows = []

        for row in df.itertuples(
            index=False,
            name=None
        ):

            cleaned_row = []

            for value in row:

                if pd.isna(value):

                    cleaned_row.append(None)

                elif isinstance(
                    value,
                    pd.Timestamp
                ):

                    cleaned_row.append(
                        value.to_pydatetime()
                    )

                else:

                    cleaned_row.append(value)

            rows.append(
                tuple(cleaned_row)
            )

        with connection.cursor() as cursor:

            cursor.executemany(
                insert_query,
                rows
            )

        connection.commit()

        return len(rows)

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()