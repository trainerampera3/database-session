import pandas as pd
import psycopg

CSV_FILE = "../../data/raw/ai_jobs_market_2025_2026_uncleaned.csv"

BATCH_SIZE = 100

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS batch_log (
    run_id VARCHAR PRIMARY KEY,
    pipeline_started TIMESTAMP,
    completed TIMESTAMP,
    status VARCHAR,
    records INTEGER,
    error TEXT
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id VARCHAR PRIMARY KEY,
    job_title VARCHAR,
    job_category VARCHAR,
    experience_level VARCHAR,
    years_of_experience INTEGER,
    education_required VARCHAR,
    city VARCHAR,
    country VARCHAR,
    remote_work VARCHAR,
    company_size VARCHAR,
    industry VARCHAR,
    required_skills TEXT
);

CREATE TABLE IF NOT EXISTS jobs_market (
    job_id VARCHAR PRIMARY KEY,
    is_senior BOOLEAN,
    is_remote_friendly BOOLEAN,
    is_llm_role BOOLEAN,
    annual_salary_usd NUMERIC,
    salary_min_usd NUMERIC,
    salary_max_usd NUMERIC,
    ai_salary_premium_pct NUMERIC,
    demand_score INTEGER,
    demand_growth_yoy_pct NUMERIC,
    benefits_score_10 NUMERIC,
    posting_year INTEGER,
    posting_month INTEGER,
    CONSTRAINT fk_job
        FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
        ON DELETE CASCADE
);
"""

PROCEDURE_SQL = """
CREATE OR REPLACE PROCEDURE process_job_batch(job_batch jsonb)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO jobs (
        job_id,
        job_title,
        job_category,
        experience_level,
        years_of_experience,
        education_required,
        city,
        country,
        remote_work,
        company_size,
        industry,
        required_skills
    )
    SELECT
        payload->>'job_id',
        payload->>'job_title',
        payload->>'job_category',
        payload->>'experience_level',
        NULLIF(payload->>'years_of_experience', '')::integer,
        payload->>'education_required',
        payload->>'city',
        payload->>'country',
        payload->>'remote_work',
        payload->>'company_size',
        payload->>'industry',
        payload->>'required_skills'
    FROM jsonb_array_elements(job_batch) AS payload
    WHERE NOT EXISTS (
        SELECT 1 FROM jobs j WHERE j.job_id = payload->>'job_id'
    );

    INSERT INTO jobs_market (
        job_id,
        is_senior,
        is_remote_friendly,
        is_llm_role,
        annual_salary_usd,
        salary_min_usd,
        salary_max_usd,
        ai_salary_premium_pct,
        demand_score,
        demand_growth_yoy_pct,
        benefits_score_10,
        posting_year,
        posting_month
    )
    SELECT
        payload->>'job_id',
        NULLIF(payload->>'is_senior', '')::boolean,
        NULLIF(payload->>'is_remote_friendly', '')::boolean,
        NULLIF(payload->>'is_llm_role', '')::boolean,
        NULLIF(payload->>'annual_salary_usd', '')::numeric,
        NULLIF(payload->>'salary_min_usd', '')::numeric,
        NULLIF(payload->>'salary_max_usd', '')::numeric,
        NULLIF(payload->>'ai_salary_premium_pct', '')::numeric,
        NULLIF(payload->>'demand_score', '')::integer,
        NULLIF(payload->>'demand_growth_yoy_pct', '')::numeric,
        NULLIF(payload->>'benefits_score_10', '')::numeric,
        NULLIF(payload->>'posting_year', '')::integer,
        NULLIF(payload->>'posting_month', '')::integer
    FROM jsonb_array_elements(job_batch) AS payload
    WHERE NOT EXISTS (
        SELECT 1 FROM jobs_market jm WHERE jm.job_id = payload->>'job_id'
    );
END;
$$;
"""

def get_connection():

    return psycopg.connect(
        host="localhost",
        port=5433,
        dbname="job_management",
        user="deepika",
        password="deepu1014"
    )


def ensure_schema(conn):
    with conn.cursor() as cursor:
                   
        cursor.execute(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'batch_log'
                ) THEN
                    IF EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name = 'batch_log'
                          AND column_name = 'run_id'
                          AND data_type != 'character varying'
                    ) THEN
                        DROP TABLE batch_log CASCADE;
                    END IF;
                END IF;
            END $$;
            """
        )
        cursor.execute(SCHEMA_SQL)
        cursor.execute(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'jobs'
                      AND column_name IN ('is_senior', 'is_remote_friendly', 'is_llm_role')
                ) THEN
                    ALTER TABLE jobs DROP COLUMN IF EXISTS is_senior;
                    ALTER TABLE jobs DROP COLUMN IF EXISTS is_remote_friendly;
                    ALTER TABLE jobs DROP COLUMN IF EXISTS is_llm_role;
                END IF;

                IF EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'jobs_market'
                      AND column_name = 'job_id'
                ) AND NOT EXISTS (
                    SELECT 1
                    FROM pg_constraint
                    WHERE conrelid = 'jobs_market'::regclass
                      AND contype = 'p'
                ) THEN
                    ALTER TABLE jobs_market ADD PRIMARY KEY (job_id);
                END IF;

                IF NOT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'jobs_market'
                      AND column_name = 'is_senior'
                ) THEN
                    ALTER TABLE jobs_market ADD COLUMN is_senior BOOLEAN;
                END IF;

                IF NOT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'jobs_market'
                      AND column_name = 'is_remote_friendly'
                ) THEN
                    ALTER TABLE jobs_market ADD COLUMN is_remote_friendly BOOLEAN;
                END IF;

                IF NOT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'jobs_market'
                      AND column_name = 'is_llm_role'
                ) THEN
                    ALTER TABLE jobs_market ADD COLUMN is_llm_role BOOLEAN;
                END IF;

                CREATE UNIQUE INDEX IF NOT EXISTS jobs_market_job_id_unique
                    ON jobs_market (job_id);
            END $$;
            """
        )

def ensure_procedure(conn):
    with conn.cursor() as cursor:
        cursor.execute(PROCEDURE_SQL)



def clean_batch(batch_df):
    
    text_columns = batch_df.select_dtypes(
        include=["object", "string"]
    ).columns

    for col in text_columns:

        batch_df[col] = (
            batch_df[col]
            .astype("string")
            .str.strip()
        )

 

    integer_columns = [
        "years_of_experience",
        "posting_year",
        "demand_score",
        "posting_month"
    ]

    for col in integer_columns:

        batch_df[col] = pd.to_numeric(
            batch_df[col],
            errors="coerce"
        )

    numeric_columns = [
        "annual_salary_usd",
        "salary_min_usd",
        "salary_max_usd",
        "ai_salary_premium_pct",
        "demand_growth_yoy_pct",
        "benefits_score_10"
    ]

    for col in numeric_columns:

        batch_df[col] = pd.to_numeric(
            batch_df[col],
            errors="coerce"
        )

   
    boolean_columns = [
        "is_senior",
        "is_remote_friendly",
        "is_llm_role"
    ]

    for col in boolean_columns:

        batch_df[col] = (
            pd.to_numeric(
                batch_df[col],
                errors="coerce"
            )
            .map({
                0: False,
                1: True
            })
        )

    
    batch_df = batch_df.astype(object)

    batch_df = batch_df.where(
        pd.notna(batch_df),
        None
    )


    return batch_df




def insert_jobs(conn, batch_df):

    query = """
        INSERT INTO jobs (
            job_id,
            job_title,
            job_category,
            experience_level,
            years_of_experience,
            education_required,
            city,
            country,
            remote_work,
            company_size,
            industry,
            required_skills
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (job_id) DO NOTHING;
    """

    columns = [
        "job_id",
        "job_title",
        "job_category",
        "experience_level",
        "years_of_experience",
        "education_required",
        "city",
        "country",
        "remote_work",
        "company_size",
        "industry",
        "required_skills"
    ]

    values = [
        tuple(row)
        for row in batch_df[columns].itertuples(
            index=False,
            name=None
        )
    ]

    with conn.cursor() as cursor:

        cursor.executemany(
            query,
            values
        )


def insert_jobs_market(conn, batch_df):

    query = """
        INSERT INTO jobs_market (
            job_id,
            is_senior,
            is_remote_friendly,
            is_llm_role,
            annual_salary_usd,
            salary_min_usd,
            salary_max_usd,
            ai_salary_premium_pct,
            demand_score,
            demand_growth_yoy_pct,
            benefits_score_10,
            posting_year,
            posting_month
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT DO NOTHING;
    """

    columns = [
        "job_id",
        "is_senior",
        "is_remote_friendly",
        "is_llm_role",
        "annual_salary_usd",
        "salary_min_usd",
        "salary_max_usd",
        "ai_salary_premium_pct",
        "demand_score",
        "demand_growth_yoy_pct",
        "benefits_score_10",
        "posting_year",
        "posting_month"
    ]

    values = [
        tuple(row)
        for row in batch_df[columns].itertuples(
            index=False,
            name=None
        )
    ]

    with conn.cursor() as cursor:

        cursor.executemany(
            query,
            values
        )

def load_data():
    conn = None

    try:

        conn = get_connection()

        print("PostgreSQL connected successfully.")
        
        total_rows = 0
        total_batches = 0
        duplicate_rows = 0
        null_rows = 0

        
        seen_job_ids = set()

        

        for batch_number, batch_df in enumerate(
            pd.read_csv(
                CSV_FILE,
                chunksize=BATCH_SIZE
            ),
            start=1
        ):

            print(
                f"\nProcessing batch {batch_number}..."
            )
            
            original_batch_rows = len(batch_df)

            

            batch_df = batch_df.drop_duplicates(
                subset=["job_id"]
            )


            duplicate_mask = batch_df["job_id"].isin(
                seen_job_ids
            )

            duplicate_rows += int(
                duplicate_mask.sum()
            )

            batch_df = batch_df[
                ~duplicate_mask
            ].copy()

            

            seen_job_ids.update(
                batch_df["job_id"].dropna()
            )

            required_columns = [
                "job_id",
                "job_title",
                "job_category",
                "experience_level"
            ]

            before_null_removal = len(batch_df)

            batch_df = batch_df.dropna(
                subset=required_columns
            )

            null_rows += (
                before_null_removal - len(batch_df)
            )

           
            if batch_df.empty:

                print(
                    f"Batch {batch_number} "
                    f"has no valid rows. Skipping."
                )

                continue

            

            batch_df = clean_batch(
                batch_df
            )
            
            insert_jobs(
                conn,
                batch_df
            )
            
            insert_jobs_market(
                conn,
                batch_df
            )
            
            conn.commit()

            
            rows_in_batch = len(batch_df)
            total_rows += rows_in_batch
            total_batches += 1

            print(
                f"Batch {batch_number} "
                f"inserted successfully."
            )

            print(
                f"Rows inserted: {rows_in_batch}"
            )


        

        print("\n====================================")
        print("DATA LOAD COMPLETED")
        print("====================================")

        print(
            f"Duplicate rows removed: "
            f"{duplicate_rows}"
        )

        print(
            f"NULL rows removed: "
            f"{null_rows}"
        )

        print(
            f"Total valid rows inserted: "
            f"{total_rows}"
        )

        print(
            f"Total batches inserted: "
            f"{total_batches}"
        )

    except Exception as e:

        print(
            f"\nERROR: {e}"
        )

        if conn is not None:

            conn.rollback()

    finally:
        if conn is not None:

            conn.close()

            print(
                "PostgreSQL connection closed."
            )



if __name__ == "__main__":

    load_data()
