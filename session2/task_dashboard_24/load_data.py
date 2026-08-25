from pathlib import Path
import pandas as pd
import psycopg


BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "ai_jobs_market_2025_2026_cleaned.csv"

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

        print(f"Database connection error: {e}")
        return None


def load_csv():

    print("CSV file:", CSV_FILE)

    df = pd.read_csv(CSV_FILE)

    print("CSV loaded successfully.")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    return df


def insert_data(connection, df):

    with connection.cursor() as cursor:


        job_data = (
            df[
                [
                    "job_id",
                    "job_title",
                    "job_category",
                    "experience_level",
                    "years_of_experience",
                    "education_required",
                    "required_skills"
                ]
            ]
            .drop_duplicates(subset=["job_id"])
        )

        for _, row in job_data.iterrows():

            cursor.execute(
                """
                INSERT INTO jobs (
                    job_id,
                    job_title,
                    job_category,
                    experience_level,
                    years_of_experience,
                    education_required,
                    required_skills
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (job_id) DO NOTHING
                """,
                (
                    row["job_id"],
                    row["job_title"],
                    row["job_category"],
                    row["experience_level"],
                    row["years_of_experience"],
                    row["education_required"],
                    row["required_skills"]
                )
            )

        print("Jobs inserted.")


        company_data = (
            df[
                [
                    "job_id",
                    "company_size",
                    "industry"
                ]
            ]
            .drop_duplicates()
        )

        for _, row in company_data.iterrows():

            cursor.execute(
                """
                INSERT INTO companies (
                    job_id,
                    company_size,
                    industry
                )
                VALUES (%s, %s, %s)
                """,
                (
                    row["job_id"],
                    row["company_size"],
                    row["industry"]
                )
            )

        print("Companies inserted.")



        location_data = (
            df[
                [
                    "job_id",
                    "city",
                    "country",
                    "remote_work"
                ]
            ]
            .drop_duplicates()
        )

        for _, row in location_data.iterrows():

            cursor.execute(
                """
                INSERT INTO locations (
                    job_id,
                    city,
                    country,
                    remote_work
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    row["job_id"],
                    row["city"],
                    row["country"],
                    row["remote_work"]
                )
            )

        print("Locations inserted.")




        salary_data = (
            df[
                [
                    "job_id",
                    "annual_salary_usd",
                    "salary_min_usd",
                    "salary_max_usd",
                    "ai_salary_premium_pct"
                ]
            ]
            .drop_duplicates()
        )

        for _, row in salary_data.iterrows():

            cursor.execute(
                """
                INSERT INTO salaries (
                    job_id,
                    annual_salary_usd,
                    salary_min_usd,
                    salary_max_usd,
                    ai_salary_premium_pct
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    row["job_id"],
                    row["annual_salary_usd"],
                    row["salary_min_usd"],
                    row["salary_max_usd"],
                    row["ai_salary_premium_pct"]
                )
            )

        print("Salaries inserted.")



        market_data = (
            df[
                [
                    "job_id",
                    "demand_score",
                    "demand_growth_yoy_pct",
                    "benefits_score_10",
                    "posting_year",
                    "posting_month",
                    "is_senior",
                    "is_remote_friendly",
                    "is_llm_role"
                ]
            ]
            .drop_duplicates()
        )

        for _, row in market_data.iterrows():

            cursor.execute(
                """
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
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    row["job_id"],
                    row["demand_score"],
                    row["demand_growth_yoy_pct"],
                    row["benefits_score_10"],
                    row["posting_year"],
                    row["posting_month"],
                    row["is_senior"],
                    row["is_remote_friendly"],
                    row["is_llm_role"]
                )
            )

        print("Job market data inserted.")


    connection.commit()

    print("All data inserted successfully.")




# df = load_csv()

# connection = create_connection()

# if connection:

#     insert_data(connection, df)

#     connection.close()

#     print("Database connection closed.")



df = load_csv()

df["is_senior"] = df["is_senior"].astype(bool)
df["is_remote_friendly"] = df["is_remote_friendly"].astype(bool)
df["is_llm_role"] = df["is_llm_role"].astype(bool)

connection = create_connection()

if connection:
    insert_data(connection, df)
    connection.close()