from utils.database_connection import connection
from datetime import timedelta
import pandas as pd
import psycopg
import csv
import logging
import uuid
'''
def load_data_using_insertions(dataframe):
    conn = connection()

    with conn.cursor() as cursor:

            
        res = []
        batch_size = 100
        i=0
        no_of_batches=0
        for row in dataframe.itertuples(index=False,name=None):
            res.append(row)
            if(len(res)==batch_size):
                cursor.executemany("""
                insert into patients values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                
                """,res)
                conn.commit()
                
                res=[]
        if res:
            cursor.executemany("""
                insert into patients values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
      
                """,res)
            conn.commit()

'''
#This is testing function to check how copy works
def load_data_using_insertions(dataframe,source_file_name,progress_callback=None):
    conn = connection()

    batch_size = 100
    total_rows = len(dataframe)
    processed_rows = 0

    try:
        with conn.cursor() as cursor:
            rows = dataframe.itertuples(index=False, name=None)

            batch = []

            for row in rows:
                batch.append(row)

                if len(batch) == batch_size:
                    with cursor.copy("""
                        COPY patients FROM STDIN
                    """) as copy:
                        for item in batch:
                            copy.write_row(item)

                    conn.commit()
                    batch_id = f"BATCH-{uuid.uuid4().hex[:8].upper()}"
                    conn.execute("""
                    
                    Insert into logs values (%s,%s,%s)
                    """,(batch_id,source_file_name,'success'))
                    conn.commit()
                    processed_rows += len(batch)
                    if progress_callback is not None:
                        progress_callback(processed_rows / total_rows)
                    batch = []

            if batch:
                batch_id = f"BATCH-{uuid.uuid4().hex[:8].upper()}"
                with cursor.copy("""
                    COPY patients FROM STDIN
                """) as copy:
                    for item in batch:
                        copy.write_row(item)

                conn.commit()
                conn.execute("""        
                Insert into logs values (%s,%s,%s)
                """,(batch_id,source_file_name,'success'))
                conn.commit()
                processed_rows += len(batch)
                if progress_callback is not None:
                    progress_callback(processed_rows / total_rows)
    finally:
        conn.close()
        return processed_rows

def insert_db(source_file, stage, rows, status,file_path):
    conn = connection()

    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO runs (
                source_file,
                target_table,
                stage,
                rows_count,
                duration,
                status,
                file_path
            )
            VALUES (%s, %s, %s, %s, %s, %s,%s)
        """, (
            source_file,
            "patients",
            stage,
            rows,
            None,
            status,
            file_path
        ))


    conn.commit()

def update_db(source_file, stage, rows, status,file_path,duration=None,processed_rows=None):
    conn = connection()
    if duration is not None:
        duration=timedelta(seconds=duration)

    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE runs
            SET stage = %s,
                rows_count = %s,
                status = %s,
                duration=%s,
                file_path=%s,
                total_rows=%s
            WHERE source_file = %s
        """, (
            stage,
            rows,
            status,
            duration,
            file_path,
            processed_rows,
            source_file
            
           
        ))

        conn.commit()



def get_runs_details():
    conn = connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    batch_id,
                    source_file,
                    target_table,
                    stage,
                    rows_count,
                   extract(epoch from duration) as time_duration,
                    status
                FROM runs
            """)

            rows = cursor.fetchall()

            return pd.DataFrame(
                rows,
                columns=[
                    "batch_id",
                    "source_file",
                    "target_table",
                    "stage",
                    "rows_count",
                    "time_duration",
                    "status"
                ]
            )

    finally:
        conn.close()




def run_qurey(query):
    result=None
    conn=connection()
    with conn.cursor() as cursor:
        cursor.execute(query)
        result=cursor.fetchall()
    cols=[]
    with conn.cursor() as cursor:
        cursor.execute("""
        
        SELECT column_name
FROM information_schema.columns
WHERE table_name = 'patients'
ORDER BY ordinal_position;

        """)
        for i in cursor.fetchall():
            cols.append(i[0])
    return pd.DataFrame(result,columns=cols)

def get_log_details():
    conn=connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            select * from logs;
        
        """)
        rows=cursor.fetchall()
        return pd.DataFrame(rows,columns=['batch_id','source_file','status'])

    