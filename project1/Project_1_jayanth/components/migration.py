import streamlit as st
import time as t
import pandas as pd
from psycopg import sql
from components.logger import logger
from datetime import datetime





def migration(conn):

    st.header("Migration")

    df = st.session_state.df
    mapping = st.session_state.mapping
    t_name = st.session_state.tname
    const = st.session_state.const
    

    if not t_name:
        st.error("Please enter a table name.")
        st.stop()

    st.write("Table name:", repr(t_name))

    if st.button('Create table', key='create_table'):
        with conn.cursor() as cur:

            query = sql.SQL(
                "DROP TABLE IF EXISTS {}"
            ).format(
                sql.Identifier(t_name)
            )
            logger.info(f"table {t_name} is Dropped")
            

            cur.execute(query)

            query = sql.SQL("""
                CREATE TABLE IF NOT EXISTS {} (
                    {}
                )
            """).format(
                sql.Identifier(t_name),
                sql.SQL(", ").join(
                    sql.SQL(column)
                    for column in const
                )
            )

            cur.execute(query)

            conn.commit()
            logger.info(f"table {t_name} is Created")

        st.success("Table successfully created")

        st.write(
            f"Rows ready for migration: {len(df):,}"
        )


    if st.button(
        "Start Migration",
        key="start_migration"
    ):

        tb = t.time()

        logger.info(f"{st.session_state.file_name} is Migrating to database")
        with conn.cursor() as cur:
            cur.execute("""update batchlog set stage = %s, status = %s, updated_at = NOW() AT TIME ZONE 'Asia/Kolkata' where batch_id = %s;""",('migrate','running',f"BAT-{st.session_state.id}"))
        conn.commit()
        

        progress = st.progress(0)

        failed_rows = []

        batch_size = 10000

        db_columns = list(mapping.values())
        csv_columns = list(mapping.keys())


        with conn.cursor() as cur:

            for start in range(0, len(df), batch_size):

                batch = df.iloc[
                    start:start + batch_size
                ]

                query = sql.SQL("""
                    INSERT INTO {} ({})
                    VALUES ({})
                """).format(

                    sql.Identifier(t_name),

                    sql.SQL(", ").join(
                        sql.Identifier(col)
                        for col in db_columns
                    ),

                    sql.SQL(", ").join(
                        sql.Placeholder()
                        for _ in db_columns
                    )
                )

                
                values = list(
                    batch[
                        csv_columns
                    ].itertuples(
                        index=False,
                        name=None
                    )
                )

                batch_number = (start // batch_size) + 1

                try:
                    cur.executemany(query,values)
                    conn.commit()
                    logger.info(f"Batch {batch_number} inserted successfully for file {st.session_state.file_name}")

                except Exception as batch_error:
                    conn.rollback()

                    st.warning(
                        f"Batch {batch_number} failed. "
                        f"Checking individual rows..."
                    )
                    logger.error(f"Batch {batch_number} failed: {batch_error}")

                    # Try rows individually
                    for row_index, row in enumerate(values,start=start):

                        try:

                            cur.execute(query,row)
                            conn.commit()

                        except Exception as row_error:

                            conn.rollback()
                            logger.error(f"Row {row_index + 1} failed: {row_error}")

                            failed_rows.append({

                                "row_number":
                                    row_index + 1,

                                "error":
                                    str(row_error),

                                "data":
                                    row
                            })
                    

                progress.progress(
                    min((start + len(batch)) / len(df), 1.0)
                )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = st.session_state.file_name
        output_file = f"{file_name}_{timestamp}"
        df.to_csv(f"uploads/{output_file}", index=False)
        logger.info(f"{file_name} is successfully saved into processed")
        ta = t.time()

        if failed_rows:

            st.warning(
                f"Migration completed with "
                f"{len(failed_rows)} rejected rows."
            )

        else:

            st.success(
                "Migration completed successfully!"
            )
            st.session_state.success += len(df)

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Rows inserted",
                len(df) - len(failed_rows)
            )

        with col2:

            st.metric(
                "Rows rejected",
                len(failed_rows)
            )
            st.session_state.failed += len(failed_rows)

        with col3:

            st.metric(
                "Duration",
                f"{ta - tb:.2f} seconds"
            )

            with conn.cursor() as cur:
                cur.execute("""update batchlog set stage = %s, rows = %s,duration = %s , status = %s, updated_at = NOW() AT TIME ZONE 'Asia/Kolkata'  where batch_id = %s;""",('Migrate',len(df)-len(failed_rows),round(ta - tb,2),'succeded',f"BAT-{st.session_state.id}"))
            conn.commit()
            

        if failed_rows:

            st.subheader("Rejected Rows")

            failed_df = pd.DataFrame(
                failed_rows
            )

            st.dataframe(
                failed_df,
                use_container_width=True
            )