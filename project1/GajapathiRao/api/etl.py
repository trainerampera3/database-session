from pathlib import Path
from uuid import uuid4

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from ETL.preprocessing.clean import clean_dataframe
from ETL.preprocessing.profile import profile_dataframe
from ETL.preprocessing.transform import apply_transformations
from ETL.preprocessing.migrate import migrate_dataframe


router = APIRouter(
    prefix="/api/etl",
    tags=["ETL"],
)


BASE_DIR = Path(__file__).resolve().parents[2]
JOB_DIR = BASE_DIR / "etl_jobs"

JOB_DIR.mkdir(
    exist_ok=True
)


# ---------------------------------------------------------
# REQUEST MODELS
# ---------------------------------------------------------

class CleaningRequest(BaseModel):

    missing_action: str = "none"

    remove_duplicates: bool = False


class TransformationRequest(BaseModel):

    rename_map: dict[str, str] | None = None

    remove_columns: list[str] | None = None

    type_map: dict[str, str] | None = None


class MigrationRequest(BaseModel):

    table_name: str


# ---------------------------------------------------------
# HELPER
# ---------------------------------------------------------

def get_job_directory(
    job_id: str,
) -> Path:

    job_directory = JOB_DIR / job_id

    if not job_directory.exists():

        raise HTTPException(
            status_code=404,
            detail="ETL job not found.",
        )

    return job_directory


def load_job_dataframe(
    job_id: str,
    filename: str,
) -> pd.DataFrame:

    job_directory = get_job_directory(
        job_id
    )

    file_path = job_directory / filename

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail=f"{filename} not found.",
        )

    return pd.read_csv(
        file_path,
        sep=None,
        engine="python",
    )


# ---------------------------------------------------------
# 1. UPLOAD
# ---------------------------------------------------------

@router.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="File name is required.",
        )

    if not file.filename.lower().endswith(
        ".csv"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported.",
        )

    try:

        contents = await file.read()

        from io import BytesIO

        df = pd.read_csv(
            BytesIO(contents),
            sep=None,
            engine="python",
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=f"Unable to read CSV file: {exc}",
        )

    if df.empty:

        raise HTTPException(
            status_code=400,
            detail="Uploaded CSV is empty.",
        )

    job_id = str(uuid4())

    job_directory = JOB_DIR / job_id

    job_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    original_path = (
        job_directory / "original.csv"
    )

    df.to_csv(
        original_path,
        index=False,
    )

    profile = profile_dataframe(df)

    return {
        "success": True,
        "job_id": job_id,
        "filename": file.filename,
        "profile": profile,
        "preview": df.head(20)
        .astype(object)
        .where(pd.notna(df.head(20)), None)
        .to_dict(orient="records"),
    }


# ---------------------------------------------------------
# 2. CLEAN
# ---------------------------------------------------------

@router.post("/{job_id}/clean")
def clean_data(
    job_id: str,
    request: CleaningRequest,
):

    df = load_job_dataframe(
        job_id,
        "original.csv",
    )

    try:

        cleaned_df = clean_dataframe(
            df,
            missing_action=request.missing_action,
            remove_duplicates=request.remove_duplicates,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    cleaned_path = (
        get_job_directory(job_id)
        / "cleaned.csv"
    )

    cleaned_df.to_csv(
        cleaned_path,
        index=False,
    )

    profile = profile_dataframe(
        cleaned_df
    )

    return {
        "success": True,
        "job_id": job_id,
        "profile": profile,
        "preview": cleaned_df.head(20)
        .astype(object)
        .where(
            pd.notna(cleaned_df.head(20)),
            None,
        )
        .to_dict(
            orient="records"
        ),
    }


# ---------------------------------------------------------
# 3. TRANSFORM
# ---------------------------------------------------------

@router.post("/{job_id}/transform")
def transform_data(
    job_id: str,
    request: TransformationRequest,
):

    cleaned_path = (
        get_job_directory(job_id)
        / "cleaned.csv"
    )

    if not cleaned_path.exists():

        raise HTTPException(
            status_code=400,
            detail=(
                "Please clean the dataset "
                "before applying transformations."
            ),
        )

    df = pd.read_csv(
        cleaned_path,
        sep=None,
        engine="python",
    )

    try:

        transformed_df = apply_transformations(
            df,
            rename_map=request.rename_map,
            remove_columns_list=request.remove_columns,
            type_map=request.type_map,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    transformed_path = (
        get_job_directory(job_id)
        / "transformed.csv"
    )

    transformed_df.to_csv(
        transformed_path,
        index=False,
    )

    profile = profile_dataframe(
        transformed_df
    )

    return {
        "success": True,
        "job_id": job_id,
        "profile": profile,
        "columns": [
            str(column)
            for column in transformed_df.columns
        ],
        "preview": transformed_df.head(20)
        .astype(object)
        .where(
            pd.notna(transformed_df.head(20)),
            None,
        )
        .to_dict(
            orient="records"
        ),
    }


# ---------------------------------------------------------
# 4. MIGRATE
# ---------------------------------------------------------

@router.post("/{job_id}/migrate")
def migrate_data(
    job_id: str,
    request: MigrationRequest,
):

    transformed_path = (
        get_job_directory(job_id)
        / "transformed.csv"
    )

    if not transformed_path.exists():

        raise HTTPException(
            status_code=400,
            detail=(
                "Please transform the dataset "
                "before migration."
            ),
        )

    df = pd.read_csv(
        transformed_path,
        sep=None,
        engine="python",
    )

    try:

        rows_migrated = migrate_dataframe(
            df,
            request.table_name,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Migration failed: {exc}",
        )

    return {
        "success": True,
        "message": "Dataset migrated successfully.",
        "table_name": request.table_name,
        "rows_migrated": rows_migrated,
    }