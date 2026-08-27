from pathlib import Path
import json

import pandas as pd
import psycopg
from psycopg.types.json import Jsonb

BASE_DIR = Path(__file__).resolve().parent

CSV_FILE = BASE_DIR / "ai_jobs_market_2025_2026_cleaned.csv"

BATCH_SIZE = 100


def create_connection():

    try:

        connection = psycopg.connect(
            host="localhost",
            port="5433",
            dbname="job",
            user="deepika",
            password="deepu1014"
        )

        print("Database connection successful.")

        return connection

    except Exception as e:

        print("Database connection error:", e)

        return None



def create_stored_procedure(connection):

    procedure_sql = """
    CREATE OR REPLACE PROCEDURE process_job_batch(
        p_batch JSONB
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN

        -- JOBS
        INSERT INTO jobs (
            job_id,
            job_title,
            job_category,
            experience_level,
            years_of_experience,
            education_required,
            required_skills
        )
        SELECT
            job_id,
            job_title,
            job_category,
            experience_level,
            years_of_experience,
            education_required,
            required_skills
        FROM jsonb_to_recordset(p_batch) AS x(
            job_id VARCHAR(50),
            job_title VARCHAR(255),
            job_category VARCHAR(100),
            experience_level VARCHAR(50),
            years_of_experience INTEGER,
            education_required VARCHAR(255),
            required_skills TEXT,
            company_size VARCHAR(50),
            industry VARCHAR(150),
            city VARCHAR(100),
            country VARCHAR(100),
            remote_work VARCHAR(50),
            annual_salary_usd NUMERIC,
            salary_min_usd NUMERIC,
            salary_max_usd NUMERIC,
            ai_salary_premium_pct NUMERIC,
            demand_score INTEGER,
            demand_growth_yoy_pct NUMERIC,
            benefits_score_10 NUMERIC,
            posting_year INTEGER,
            posting_month INTEGER,
            is_senior BOOLEAN,
            is_remote_friendly BOOLEAN,
            is_llm_role BOOLEAN
        );


        -- COMPANIES
        INSERT INTO companies (
            job_id,
            company_size,
            industry
        )
        SELECT
            job_id,
            company_size,
            industry
        FROM jsonb_to_recordset(p_batch) AS x(
            job_id VARCHAR(50),
            job_title VARCHAR(255),
            job_category VARCHAR(100),
            experience_level VARCHAR(50),
            years_of_experience INTEGER,
            education_required VARCHAR(255),
            required_skills TEXT,
            company_size VARCHAR(50),
            industry VARCHAR(150),
            city VARCHAR(100),
            country VARCHAR(100),
            remote_work VARCHAR(50),
            annual_salary_usd NUMERIC,
            salary_min_usd NUMERIC,
            salary_max_usd NUMERIC,
            ai_salary_premium_pct NUMERIC,
            demand_score INTEGER,
            demand_growth_yoy_pct NUMERIC,
            benefits_score_10 NUMERIC,
            posting_year INTEGER,
            posting_month INTEGER,
            is_senior BOOLEAN,
            is_remote_friendly BOOLEAN,
            is_llm_role BOOLEAN
        );


        -- LOCATIONS
        INSERT INTO locations (
            job_id,
            city,
            country,
            remote_work
        )
        SELECT
            job_id,
            city,
            country,
            remote_work
        FROM jsonb_to_recordset(p_batch) AS x(
            job_id VARCHAR(50),
            job_title VARCHAR(255),
            job_category VARCHAR(100),
            experience_level VARCHAR(50),
            years_of_experience INTEGER,
            education_required VARCHAR(255),
            required_skills TEXT,
            company_size VARCHAR(50),
            industry VARCHAR(150),
            city VARCHAR(100),
            country VARCHAR(100),
            remote_work VARCHAR(50),
            annual_salary_usd NUMERIC,
            salary_min_usd NUMERIC,
            salary_max_usd NUMERIC,
            ai_salary_premium_pct NUMERIC,
            demand_score INTEGER,
            demand_growth_yoy_pct NUMERIC,
            benefits_score_10 NUMERIC,
            posting_year INTEGER,
            posting_month INTEGER,
            is_senior BOOLEAN,
            is_remote_friendly BOOLEAN,
            is_llm_role BOOLEAN
        );


        -- SALARIES
        INSERT INTO salaries (
            job_id,
            annual_salary_usd,
            salary_min_usd,
            salary_max_usd,
            ai_salary_premium_pct
        )
        SELECT
            job_id,
            annual_salary_usd,
            salary_min_usd,
            salary_max_usd,
            ai_salary_premium_pct
        FROM jsonb_to_recordset(p_batch) AS x(
            job_id VARCHAR(50),
            job_title VARCHAR(255),
            job_category VARCHAR(100),
            experience_level VARCHAR(50),
            years_of_experience INTEGER,
            education_required VARCHAR(255),
            required_skills TEXT,
            company_size VARCHAR(50),
            industry VARCHAR(150),
            city VARCHAR(100),
            country VARCHAR(100),
            remote_work VARCHAR(50),
            annual_salary_usd NUMERIC,
            salary_min_usd NUMERIC,
            salary_max_usd NUMERIC,
            ai_salary_premium_pct NUMERIC,
            demand_score INTEGER,
            demand_growth_yoy_pct NUMERIC,
            benefits_score_10 NUMERIC,
            posting_year INTEGER,
            posting_month INTEGER,
            is_senior BOOLEAN,
            is_remote_friendly BOOLEAN,
            is_llm_role BOOLEAN
        );


        -- JOB MARKET
        INSERT INTO job_market (
            job_id,
            demand_score,
            demand_growth_yoy_pct,
            benefits_score_10,
            posting_year,
            posting_month,
            is_senior,
            is_remote_friendly,
            is_llm_role
        )
        SELECT
            job_id,
            demand_score,
            demand_growth_yoy_pct,
            benefits_score_10,
            posting_year,
            posting_month,
            is_senior,
            is_remote_friendly,
            is_llm_role
        FROM jsonb_to_recordset(p_batch) AS x(
            job_id VARCHAR(50),
            job_title VARCHAR(255),
            job_category VARCHAR(100),
            experience_level VARCHAR(50),
            years_of_experience INTEGER,
            education_required VARCHAR(255),
            required_skills TEXT,
            company_size VARCHAR(50),
            industry VARCHAR(150),
            city VARCHAR(100),
            country VARCHAR(100),
            remote_work VARCHAR(50),
            annual_salary_usd NUMERIC,
            salary_min_usd NUMERIC,
            salary_max_usd NUMERIC,
            ai_salary_premium_pct NUMERIC,
            demand_score INTEGER,
            demand_growth_yoy_pct NUMERIC,
            benefits_score_10 NUMERIC,
            posting_year INTEGER,
            posting_month INTEGER,
            is_senior BOOLEAN,
            is_remote_friendly BOOLEAN,
            is_llm_role BOOLEAN
        );

    END;
    $$;
    """

    with connection.cursor() as cursor:

        cursor.execute(procedure_sql)

    connection.commit()

    print("Stored procedure created successfully.")


def load_csv():

    df = pd.read_csv(CSV_FILE)

    print("CSV loaded successfully.")
    print("Total records:", len(df))

    return df


def prepare_data(df):

    df["years_of_experience"] = pd.to_numeric(
        df["years_of_experience"],
        errors="coerce"
    )

    df["is_senior"] = df["is_senior"].astype(bool)

    df["is_remote_friendly"] = df["is_remote_friendly"].astype(bool)

    df["is_llm_role"] = df["is_llm_role"].astype(bool)

    return df


def process_batches(connection, df):

    total_records = len(df)

    total_batches = (
        total_records + BATCH_SIZE - 1
    ) // BATCH_SIZE

    print()
    print("================================")
    print("BATCH PROCESSING")
    print("================================")

    print("Total records:", total_records)
    print("Batch size:", BATCH_SIZE)
    print("Total batches:", total_batches)

    with connection.cursor() as cursor:

        for batch_number, start in enumerate(
            range(0, total_records, BATCH_SIZE),
            start=1
        ):

            end = min(
                start + BATCH_SIZE,
                total_records
            )

            batch = df.iloc[start:end].copy()

            print(
                f"Processing batch "
                f"{batch_number}/{total_batches}: "
                f"records {start + 1}-{end}"
            )

            batch_json = json.loads(
                batch.to_json(
                    orient="records"
                )
            )

            cursor.execute(
                """
                CALL process_job_batch(%s)
                """,
                (Jsonb(batch_json),)
            )

            print(
                f"Batch {batch_number} completed."
            )

        connection.commit()

    print()
    print("All batches inserted successfully.")



def main():

    df = load_csv()

    df = prepare_data(df)

    connection = create_connection()

    if connection:

        try:
            create_stored_procedure(connection)

            process_batches(
                connection,
                df
            )

        except Exception as e:

            connection.rollback()

            print("Error:", e)

        finally:

            connection.close()

            print("Database connection closed.")


if __name__ == "__main__":
    main()