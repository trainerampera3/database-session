from db import get_connection


def create_batch_log_table():
    """Create the batch log table if it does not exist."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                CREATE TABLE IF NOT EXISTS batch_log (
                    batch_id SERIAL PRIMARY KEY,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    files INTEGER NOT NULL DEFAULT 0,
                    total_rows BIGINT NOT NULL DEFAULT 0,
                    status VARCHAR(30) NOT NULL,
                    result VARCHAR(100)
                );
            """)

        conn.commit()

    finally:
        conn.close()


def start_batch(files):
    """Create a new batch record."""

    create_batch_log_table()

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO batch_log (
                    start_time,
                    files,
                    status
                )
                VALUES (
                    CURRENT_TIMESTAMP,
                    %s,
                    'Running'
                )
                RETURNING batch_id;
            """, (files,))

            batch_id = cur.fetchone()[0]

        conn.commit()

        return batch_id

    finally:
        conn.close()


def complete_batch(
    batch_id,
    total_rows
):
    """Mark a batch as successfully completed."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                UPDATE batch_log
                SET
                    end_time = CURRENT_TIMESTAMP,
                    total_rows = %s,
                    status = 'Success',
                    result = 'Completed'
                WHERE batch_id = %s;
            """, (
                total_rows,
                batch_id
            ))

        conn.commit()

    finally:
        conn.close()


def fail_batch(
    batch_id,
    error_message
):
    """Mark a batch as failed."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                UPDATE batch_log
                SET
                    end_time = CURRENT_TIMESTAMP,
                    status = 'Failed',
                    result = %s
                WHERE batch_id = %s;
            """, (
                error_message[:100],
                batch_id
            ))

        conn.commit()

    finally:
        conn.close()


def get_batch_logs():
    """Return migration history."""

    create_batch_log_table()

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    batch_id,
                    start_time,
                    end_time,
                    files,
                    total_rows,
                    status,
                    result
                FROM batch_log
                ORDER BY batch_id DESC;
            """)

            rows = cur.fetchall()

            return [
                {
                    "batch_id": row[0],
                    "start_time": row[1],
                    "end_time": row[2],
                    "files": row[3],
                    "total_rows": row[4],
                    "status": row[5],
                    "result": row[6],
                }
                for row in rows
            ]

    finally:
        conn.close()