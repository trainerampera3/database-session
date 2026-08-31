from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db import create_connection

router = APIRouter(tags=["etl"])


@router.get("/etl/logs")
def get_etl_logs():
    connection = create_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    run_id,
                    pipeline_name,
                    started_at,
                    completed_at,
                    status,
                    records_processed,
                    error_message
                FROM etl_run_log
                ORDER BY started_at DESC;
                """
            )
            rows = cursor.fetchall()
            columns = [
                "run_id",
                "pipeline_name",
                "started_at",
                "completed_at",
                "status",
                "records_processed",
                "error_message",
            ]
            data = [dict(zip(columns, row)) for row in rows]
            return {"count": len(data), "data": data}
    finally:
        connection.close()


class QueryRequest(BaseModel):
    query: str


@router.post("/query")
def execute_query(request: QueryRequest):
    query = request.query.strip()

    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    if not query.lower().startswith("select"):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed.")

    connection = create_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            data = [dict(zip(columns, row)) for row in rows]
            return {"count": len(data), "data": data}
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    finally:
        connection.close()
