import pandas as pd


def load_data(conn, file_path, table_name):

    data = pd.read_csv(file_path)

    columns = ", ".join(data.columns)

    with conn.cursor() as cur:

        with cur.copy(f"""
            COPY {table_name} ({columns})
            FROM STDIN
        """) as copy:

            for row in data.itertuples(
                index=False,
                name=None
            ):
                copy.write_row(row)

    conn.commit()