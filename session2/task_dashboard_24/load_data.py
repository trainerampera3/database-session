# from pathlib import Path
# import pandas as pd
# import psycopg


# BASE_DIR = Path(__file__).resolve().parent

# CSV_FILE = BASE_DIR / "ai_jobs_market_2025_2026_cleaned.csv"



# def create_connection():

#     try:
#         connection = psycopg.connect(
#             host="localhost",
#             port="5433",
#             dbname="job",
#             user="deepika",
#             password="deepu1014"
#         )

#         print("Database connection successful.")
#         return connection

#     except Exception as e:

#         print(f"Database connection error: {e}")
#         return None




# def load_csv():

#     print("CSV file:", CSV_FILE)

#     df = pd.read_csv(CSV_FILE)

#     print("CSV loaded successfully.")
#     print("Rows:", len(df))
#     print("Columns:", len(df.columns))

#     return df



# def insert_data(connection, df):

#     with connection.cursor() as cursor:

       

#         job_data = (
#             df[
#                 [
#                     "job_id",
#                     "job_title",
#                     "job_category",
#                     "experience_level",
#                     "years_of_experience",
#                     "education_required",
#                     "required_skills",
#                     "is_senior",
#                     "is_remote_friendly",
#                     "is_llm_role"
#                 ]
#             ]
#             .drop_duplicates(subset=["job_id"])
#             .reset_index(drop=True)
#         )

#         job_data["job_key"] = [
#             f"JOB_{i:06d}"
#             for i in range(1, len(job_data) + 1)
#         ]

#         for _, row in job_data.iterrows():

#             cursor.execute(
#                 """
#                 INSERT INTO job_dim (
#                     job_key,
#                     job_id,
#                     job_title,
#                     job_category,
#                     experience_level,
#                     years_of_experience,
#                     education_required,
#                     required_skills,
#                     is_senior,
#                     is_remote_friendly,
#                     is_llm_role
#                 )
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#                 ON CONFLICT (job_id) DO NOTHING
#                 """,
#                 (
#                     row["job_key"],
#                     row["job_id"],
#                     row["job_title"],
#                     row["job_category"],
#                     row["experience_level"],
#                     row["years_of_experience"],
#                     row["education_required"],
#                     row["required_skills"],
#                     row["is_senior"],
#                     row["is_remote_friendly"],
#                     row["is_llm_role"]
#                 )
#             )


#         company_data = (
#             df[
#                 [
#                     "company_size",
#                     "industry"
#                 ]
#             ]
#             .drop_duplicates()
#             .reset_index(drop=True)
#         )

#         company_data["company_key"] = [
#             f"COM_{i:06d}"
#             for i in range(1, len(company_data) + 1)
#         ]

#         for _, row in company_data.iterrows():

#             cursor.execute(
#                 """
#                 INSERT INTO company_dim (
#                     company_key,
#                     company_size,
#                     industry
#                 )
#                 VALUES (%s, %s, %s)
#                 ON CONFLICT DO NOTHING
#                 """,
#                 (
#                     row["company_key"],
#                     row["company_size"],
#                     row["industry"]
#                 )
#             )


    

#         location_data = (
#             df[
#                 [
#                     "city",
#                     "country"
#                 ]
#             ]
#             .drop_duplicates()
#             .reset_index(drop=True)
#         )

#         location_data["location_key"] = [
#             f"LOC_{i:06d}"
#             for i in range(1, len(location_data) + 1)
#         ]

#         for _, row in location_data.iterrows():

#             cursor.execute(
#                 """
#                 INSERT INTO location_dim (
#                     location_key,
#                     city,
#                     country
#                 )
#                 VALUES (%s, %s, %s)
#                 ON CONFLICT DO NOTHING
#                 """,
#                 (
#                     row["location_key"],
#                     row["city"],
#                     row["country"]
#                 )
#             )



#         time_data = (
#             df[
#                 [
#                     "posting_year",
#                     "posting_month"
#                 ]
#             ]
#             .drop_duplicates()
#             .reset_index(drop=True)
#         )

#         time_data["time_key"] = [
#             f"TIME_{i:06d}"
#             for i in range(1, len(time_data) + 1)
#         ]

#         for _, row in time_data.iterrows():

#             cursor.execute(
#                 """
#                 INSERT INTO time_dim (
#                     time_key,
#                     posting_year,
#                     posting_month
#                 )
#                 VALUES (%s, %s, %s)
#                 ON CONFLICT DO NOTHING
#                 """,
#                 (
#                     row["time_key"],
#                     row["posting_year"],
#                     row["posting_month"]
#                 )
#             )



#         job_lookup = dict(
#             zip(
#                 job_data["job_id"],
#                 job_data["job_key"]
#             )
#         )

#         company_lookup = {
#             (row["company_size"], row["industry"]): row["company_key"]
#             for _, row in company_data.iterrows()
#         }

#         location_lookup = {
#             (row["city"], row["country"]): row["location_key"]
#             for _, row in location_data.iterrows()
#         }

#         time_lookup = {
#             (row["posting_year"], row["posting_month"]): row["time_key"]
#             for _, row in time_data.iterrows()
#         }


    
#         for _, row in df.iterrows():

#             job_key = job_lookup[row["job_id"]]

#             company_key = company_lookup[
#                 (
#                     row["company_size"],
#                     row["industry"]
#                 )
#             ]

#             location_key = location_lookup[
#                 (
#                     row["city"],
#                     row["country"]
#                 )
#             ]

#             time_key = time_lookup[
#                 (
#                     row["posting_year"],
#                     row["posting_month"]
#                 )
#             ]

#             cursor.execute(
#                 """
#                 INSERT INTO job_fact (
#                     job_key,
#                     company_key,
#                     location_key,
#                     time_key,
#                     annual_salary_usd,
#                     salary_min_usd,
#                     salary_max_usd,
#                     remote_work,
#                     ai_salary_premium_pct,
#                     demand_score,
#                     demand_growth_yoy_pct,
#                     benefits_score_10
#                 )
#                 VALUES (
#                     %s, %s, %s, %s,
#                     %s, %s, %s, %s,
#                     %s, %s, %s, %s
#                 )
#                 """,
#                 (
#                     job_key,
#                     company_key,
#                     location_key,
#                     time_key,
#                     row["annual_salary_usd"],
#                     row["salary_min_usd"],
#                     row["salary_max_usd"],
#                     row["remote_work"],
#                     row["ai_salary_premium_pct"],
#                     row["demand_score"],
#                     row["demand_growth_yoy_pct"],
#                     row["benefits_score_10"]
#                 )
#             )

#     connection.commit()

#     print("Data inserted successfully.")



# df = load_csv()

# connection = create_connection()

# if connection:

#     insert_data(connection, df)

#     connection.close()

#     print("Database connection closed.")






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

        # ============================================================
        # 1. JOBS
        # ============================================================

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


        # ============================================================
        # 2. COMPANIES
        # ============================================================

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


        # ============================================================
        # 3. LOCATIONS
        # ============================================================

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


        # ============================================================
        # 4. SALARIES
        # ============================================================

        salary_data = (
            df[
                [
                    "job_id",
                    "annual_salary_usd",
                    "salary_min_usd",
                    "salary_max_usd",
                    "ai_salary_premium_pct",
                    "salary_tier"
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
                    ai_salary_premium_pct,
                    salary_tier
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    row["job_id"],
                    row["annual_salary_usd"],
                    row["salary_min_usd"],
                    row["salary_max_usd"],
                    row["ai_salary_premium_pct"],
                    row["salary_tier"]
                )
            )

        print("Salaries inserted.")


        # ============================================================
        # 5. JOB MARKET
        # ============================================================

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




df = load_csv()

connection = create_connection()

if connection:

    insert_data(connection, df)

    connection.close()

    print("Database connection closed.")