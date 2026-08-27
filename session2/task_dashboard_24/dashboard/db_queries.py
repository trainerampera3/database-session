import psycopg
DB_CONFIG = {
    "host": "localhost",
    "port": "5433",
    "dbname": "job",
    "user": "deepika",
    "password": "deepu1014",
}

def run_query(query, params=None):

    with psycopg.connect(**DB_CONFIG) as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                params or ()
            )

            rows = cursor.fetchall()

            columns = [
                column.name
                for column in cursor.description
            ]

            return [
                dict(zip(columns, row))
                for row in rows
            ]

def get_overview_filters():

    query = """
        SELECT
            job_category,
            experience_level,
            company_size,
            industry,
            country,
            remote_work,
            posting_year
        FROM jobs j

        LEFT JOIN companies c
            ON c.job_id = j.job_id

        LEFT JOIN locations l
            ON l.job_id = j.job_id

        LEFT JOIN job_market m
            ON m.job_id = j.job_id
    """

    return run_query(query)


def get_jobs_by_category(filters):

    query = """
        SELECT
            j.job_category,
            COUNT(*) AS number_of_jobs

        FROM jobs j

        LEFT JOIN companies c
            ON c.job_id = j.job_id

        LEFT JOIN locations l
            ON l.job_id = j.job_id

        LEFT JOIN job_market m
            ON m.job_id = j.job_id

        WHERE 1=1
    """

    params = []

    if filters["category"]:
        query += " AND j.job_category = ANY(%s)"
        params.append(filters["category"])

    if filters["experience"]:
        query += " AND j.experience_level = ANY(%s)"
        params.append(filters["experience"])

    if filters["industry"]:
        query += " AND c.industry = ANY(%s)"
        params.append(filters["industry"])

    if filters["country"]:
        query += " AND l.country = ANY(%s)"
        params.append(filters["country"])

    if filters["remote"]:
        query += " AND l.remote_work = ANY(%s)"
        params.append(filters["remote"])

    if filters["year"]:
        query += " AND m.posting_year = ANY(%s)"
        params.append(filters["year"])

    query += """
        GROUP BY j.job_category
        ORDER BY number_of_jobs DESC
    """

    return run_query(query, params)
    

def get_jobs_by_experience(filters):

    query = """
        SELECT
            j.experience_level,
            COUNT(*) AS number_of_jobs

        FROM jobs j

        LEFT JOIN companies c
            ON c.job_id = j.job_id

        LEFT JOIN locations l
            ON l.job_id = j.job_id

        LEFT JOIN job_market m
            ON m.job_id = j.job_id

        WHERE 1=1
    """

    params = []

    if filters["category"]:
        query += " AND j.job_category = ANY(%s)"
        params.append(filters["category"])

    if filters["experience"]:
        query += " AND j.experience_level = ANY(%s)"
        params.append(filters["experience"])

    if filters["industry"]:
        query += " AND c.industry = ANY(%s)"
        params.append(filters["industry"])

    if filters["country"]:
        query += " AND l.country = ANY(%s)"
        params.append(filters["country"])

    if filters["remote"]:
        query += " AND l.remote_work = ANY(%s)"
        params.append(filters["remote"])

    if filters["year"]:
        query += " AND m.posting_year = ANY(%s)"
        params.append(filters["year"])

    query += """
        GROUP BY j.experience_level
        ORDER BY number_of_jobs DESC
    """

    return run_query(query, params)


def get_remote_work(filters):

    query = """
        SELECT
            l.remote_work,
            COUNT(*) AS number_of_jobs

        FROM jobs j

        LEFT JOIN companies c
            ON c.job_id = j.job_id

        LEFT JOIN locations l
            ON l.job_id = j.job_id

        LEFT JOIN job_market m
            ON m.job_id = j.job_id

        WHERE 1=1
    """

    params = []

    if filters["category"]:
        query += " AND j.job_category = ANY(%s)"
        params.append(filters["category"])

    if filters["experience"]:
        query += " AND j.experience_level = ANY(%s)"
        params.append(filters["experience"])

    if filters["industry"]:
        query += " AND c.industry = ANY(%s)"
        params.append(filters["industry"])

    if filters["country"]:
        query += " AND l.country = ANY(%s)"
        params.append(filters["country"])

    if filters["remote"]:
        query += " AND l.remote_work = ANY(%s)"
        params.append(filters["remote"])

    if filters["year"]:
        query += " AND m.posting_year = ANY(%s)"
        params.append(filters["year"])

    query += """
        GROUP BY l.remote_work
        ORDER BY number_of_jobs DESC
    """

    return run_query(query, params)


def get_jobs_by_industry(filters):

    query = """
        SELECT
            c.industry,
            COUNT(*) AS number_of_jobs

        FROM jobs j

        LEFT JOIN companies c
            ON c.job_id = j.job_id

        LEFT JOIN locations l
            ON l.job_id = j.job_id

        LEFT JOIN job_market m
            ON m.job_id = j.job_id

        WHERE 1=1
    """

    params = []

    if filters["category"]:
        query += " AND j.job_category = ANY(%s)"
        params.append(filters["category"])

    if filters["experience"]:
        query += " AND j.experience_level = ANY(%s)"
        params.append(filters["experience"])

    if filters["industry"]:
        query += " AND c.industry = ANY(%s)"
        params.append(filters["industry"])

    if filters["country"]:
        query += " AND l.country = ANY(%s)"
        params.append(filters["country"])

    if filters["remote"]:
        query += " AND l.remote_work = ANY(%s)"
        params.append(filters["remote"])

    if filters["year"]:
        query += " AND m.posting_year = ANY(%s)"
        params.append(filters["year"])

    query += """
        GROUP BY c.industry
        ORDER BY number_of_jobs DESC
        LIMIT 15
    """

    return run_query(query, params)

def get_jobs_by_country(filters):

    query = """
        SELECT
            l.country,
            COUNT(*) AS number_of_jobs

        FROM jobs j

        LEFT JOIN companies c
            ON c.job_id = j.job_id

        LEFT JOIN locations l
            ON l.job_id = j.job_id

        LEFT JOIN job_market m
            ON m.job_id = j.job_id

        WHERE 1=1
    """

    params = []

    if filters["category"]:
        query += " AND j.job_category = ANY(%s)"
        params.append(filters["category"])

    if filters["experience"]:
        query += " AND j.experience_level = ANY(%s)"
        params.append(filters["experience"])

    if filters["industry"]:
        query += " AND c.industry = ANY(%s)"
        params.append(filters["industry"])

    if filters["country"]:
        query += " AND l.country = ANY(%s)"
        params.append(filters["country"])

    if filters["remote"]:
        query += " AND l.remote_work = ANY(%s)"
        params.append(filters["remote"])

    if filters["year"]:
        query += " AND m.posting_year = ANY(%s)"
        params.append(filters["year"])

    query += """
        GROUP BY l.country

        ORDER BY number_of_jobs DESC

        LIMIT 15
    """

    return run_query(query, params)


def get_posting_trend(filters):

    query = """
        SELECT
            m.posting_year,
            COUNT(*) AS number_of_jobs

        FROM jobs j

        LEFT JOIN companies c
            ON c.job_id = j.job_id

        LEFT JOIN locations l
            ON l.job_id = j.job_id

        LEFT JOIN job_market m
            ON m.job_id = j.job_id

        WHERE 1=1
    """

    params = []

    if filters["category"]:
        query += " AND j.job_category = ANY(%s)"
        params.append(filters["category"])

    if filters["experience"]:
        query += " AND j.experience_level = ANY(%s)"
        params.append(filters["experience"])

    if filters["industry"]:
        query += " AND c.industry = ANY(%s)"
        params.append(filters["industry"])

    if filters["country"]:
        query += " AND l.country = ANY(%s)"
        params.append(filters["country"])

    if filters["remote"]:
        query += " AND l.remote_work = ANY(%s)"
        params.append(filters["remote"])

    if filters["year"]:
        query += " AND m.posting_year = ANY(%s)"
        params.append(filters["year"])

    query += """
        GROUP BY m.posting_year

        ORDER BY m.posting_year
    """

    return run_query(query, params)


def get_salary_filters():

    query = """
        SELECT DISTINCT
            j.job_category,
            j.job_title,
            j.experience_level,
            c.company_size,
            c.industry,
            j.years_of_experience,
            s.annual_salary_usd

        FROM jobs j

        LEFT JOIN companies c
            ON c.job_id = j.job_id

        LEFT JOIN salaries s
            ON s.job_id = j.job_id

        ORDER BY
            j.job_category,
            j.job_title,
            j.experience_level,
            c.company_size,
            c.industry
    """

    return run_query(query)


def get_average_salary_by_experience(filters):

    query = """
        SELECT
            j.experience_level,
            AVG(s.annual_salary_usd) AS average_salary

        FROM jobs j

        LEFT JOIN salaries s
            ON s.job_id = j.job_id

        LEFT JOIN companies c
            ON c.job_id = j.job_id

        WHERE 1=1
    """

    params = []

    if filters["experience"]:
        query += " AND j.experience_level = ANY(%s)"
        params.append(filters["experience"])

    if filters["company"]:
        query += " AND c.company_size = ANY(%s)"
        params.append(filters["company"])

    if filters["industry"]:
        query += " AND c.industry = ANY(%s)"
        params.append(filters["industry"])

    query += """
        AND j.years_of_experience BETWEEN %s AND %s
    """

    params.append(filters["years_min"])
    params.append(filters["years_max"])

    query += """
        AND s.annual_salary_usd BETWEEN %s AND %s
    """

    params.append(filters["salary_min"])
    params.append(filters["salary_max"])

    query += """
        GROUP BY j.experience_level

        ORDER BY average_salary DESC
    """

    return run_query(query, params)


def get_top_salary_roles(filters):

    query = """
        SELECT
            j.job_title,
            AVG(s.annual_salary_usd) AS average_salary

        FROM jobs j

        LEFT JOIN salaries s
            ON s.job_id = j.job_id

        LEFT JOIN companies c
            ON c.job_id = j.job_id

        WHERE 1=1
    """

    params = []

    if filters["experience"]:
        query += " AND j.experience_level = ANY(%s)"
        params.append(filters["experience"])

    if filters["company"]:
        query += " AND c.company_size = ANY(%s)"
        params.append(filters["company"])

    if filters["industry"]:
        query += " AND c.industry = ANY(%s)"
        params.append(filters["industry"])


    if filters["job_title"]:
        query += " AND j.job_title = ANY(%s)"
        params.append(filters["job_title"])

    query += """
        AND j.years_of_experience BETWEEN %s AND %s
    """

    params.append(filters["years_min"])
    params.append(filters["years_max"])

    query += """
        AND s.annual_salary_usd BETWEEN %s AND %s
    """

    params.append(filters["salary_min"])
    params.append(filters["salary_max"])

    query += """
        GROUP BY j.job_title

        ORDER BY average_salary DESC

        LIMIT 15
    """

    return run_query(query, params)


def get_average_salary_by_category(filters):

    query = """
        SELECT
            j.job_category,
            AVG(s.annual_salary_usd) AS average_salary

        FROM jobs j

        LEFT JOIN salaries s
            ON s.job_id = j.job_id

        WHERE 1=1
    """

    params = []

    if filters["category"]:
        query += " AND j.job_category = ANY(%s)"
        params.append(filters["category"])

    if filters["job_title"]:
        query += " AND j.job_title = ANY(%s)"
        params.append(filters["job_title"])

    query += """
        GROUP BY j.job_category
        ORDER BY average_salary DESC
    """

    return run_query(query, params)


def get_salary_vs_experience(filters):

    query = """
        SELECT
            j.years_of_experience,
            s.annual_salary_usd

        FROM jobs j

        LEFT JOIN salaries s
            ON s.job_id = j.job_id

        WHERE 1=1
    """

    params = []

    if filters["category"]:
        query += " AND j.job_category = ANY(%s)"
        params.append(filters["category"])

    if filters["job_title"]:
        query += " AND j.job_title = ANY(%s)"
        params.append(filters["job_title"])

    query += """
        AND j.years_of_experience IS NOT NULL
        AND s.annual_salary_usd IS NOT NULL

        ORDER BY j.years_of_experience
    """

    return run_query(query, params)



def get_salary_by_industry(filters):

    query = """
        SELECT
            c.industry,
            AVG(s.annual_salary_usd) AS average_salary

        FROM jobs j

        LEFT JOIN salaries s
            ON s.job_id = j.job_id

        LEFT JOIN companies c
            ON c.job_id = j.job_id

        WHERE 1=1
    """

    params = []

    if filters["category"]:
        query += " AND j.job_category = ANY(%s)"
        params.append(filters["category"])

    if filters["job_title"]:
        query += " AND j.job_title = ANY(%s)"
        params.append(filters["job_title"])

    query += """
        GROUP BY c.industry
        ORDER BY average_salary DESC
        LIMIT 15
    """

    return run_query(query, params)



def get_ai_salary_premium_by_category(filters):

    query = """
        SELECT
            j.job_category,
            AVG(s.ai_salary_premium_pct) AS average_ai_premium

        FROM jobs j

        LEFT JOIN salaries s
            ON s.job_id = j.job_id

        WHERE 1=1
    """

    params = []

    if filters["category"]:
        query += " AND j.job_category = ANY(%s)"
        params.append(filters["category"])

    if filters["job_title"]:
        query += " AND j.job_title = ANY(%s)"
        params.append(filters["job_title"])

    query += """
        GROUP BY j.job_category
        ORDER BY average_ai_premium DESC
    """

    return run_query(query, params)




def get_demand_filters():

    query = """
        SELECT DISTINCT
            j.job_category,
            j.job_title,
            j.experience_level,
            c.industry

        FROM jobs j

        LEFT JOIN companies c
            ON c.job_id = j.job_id

        ORDER BY
            j.job_category,
            j.job_title,
            j.experience_level,
            c.industry
    """

    return run_query(query)


def get_demand_by_role(filters):

    query = """
        SELECT
            j.job_title,
            AVG(m.demand_score) AS average_demand_score

        FROM jobs j

        LEFT JOIN job_market m
            ON m.job_id = j.job_id

        LEFT JOIN companies c
            ON c.job_id = j.job_id

        WHERE 1=1
    """

    params = []

    if filters["job_title"]:
        query += " AND j.job_title = ANY(%s)"
        params.append(filters["job_title"])

    if filters["experience"]:
        query += " AND j.experience_level = ANY(%s)"
        params.append(filters["experience"])

    if filters["industry"]:
        query += " AND c.industry = ANY(%s)"
        params.append(filters["industry"])

    if filters["senior"]:
        query += " AND m.is_senior = TRUE"

    if filters["remote"]:
        query += " AND m.is_remote_friendly = TRUE"

    if filters["llm"]:
        query += " AND m.is_llm_role = TRUE"

    query += """
        GROUP BY j.job_title

        ORDER BY average_demand_score DESC

        LIMIT 15
    """

    return run_query(query, params)


def get_llm_roles(filters):

    query = """
        SELECT
            CASE
                WHEN m.is_llm_role = TRUE
                THEN 'LLM Role'
                ELSE 'Non-LLM Role'
            END AS role_type,

            COUNT(*) AS number_of_jobs

        FROM jobs j

        LEFT JOIN job_market m
            ON m.job_id = j.job_id

        LEFT JOIN companies c
            ON c.job_id = j.job_id

        WHERE 1=1
    """

    params = []

    
    if filters["job_title"]:
        query += " AND j.job_title = ANY(%s)"
        params.append(filters["job_title"])

    if filters["experience"]:
        query += " AND j.experience_level = ANY(%s)"
        params.append(filters["experience"])

    if filters["industry"]:
        query += " AND c.industry = ANY(%s)"
        params.append(filters["industry"])

    if filters["senior"]:
        query += " AND m.is_senior = TRUE"

    if filters["remote"]:
        query += " AND m.is_remote_friendly = TRUE"

    if filters["llm"]:
        query += " AND m.is_llm_role = TRUE"

    query += """
        GROUP BY m.is_llm_role

        ORDER BY number_of_jobs DESC
    """

    return run_query(query, params)

def get_demand_growth_by_category(filters):

    query = """
        SELECT
            j.job_category,
            AVG(m.demand_growth_yoy_pct) AS average_demand_growth

        FROM jobs j

        LEFT JOIN job_market m
            ON m.job_id = j.job_id

        WHERE 1=1
    """

    params = []

    if filters["category"]:
        query += " AND j.job_category = ANY(%s)"
        params.append(filters["category"])

    query += """
        GROUP BY j.job_category

        ORDER BY average_demand_growth DESC
    """

    return run_query(query, params)


def get_senior_vs_non_senior(filters):

    query = """
        SELECT
            CASE
                WHEN m.is_senior = TRUE
                THEN 'Senior'
                ELSE 'Non-Senior'
            END AS role_type,

            COUNT(*) AS number_of_jobs

        FROM jobs j

        LEFT JOIN job_market m
            ON m.job_id = j.job_id

        WHERE 1=1
    """

    params = []

    if filters["job_title"]:
        query += " AND j.job_title = ANY(%s)"
        params.append(filters["job_title"])

    if filters["experience"]:
        query += " AND j.experience_level = ANY(%s)"
        params.append(filters["experience"])

    if filters["industry"]:
        query += " AND c.industry = ANY(%s)"
        params.append(filters["industry"])

    if filters["category"]:
        query += " AND j.job_category = ANY(%s)"
        params.append(filters["category"])

    if filters["senior"]:
        query += " AND m.is_senior = TRUE"

    if filters["remote"]:
        query += " AND m.is_remote_friendly = TRUE"

    if filters["llm"]:
        query += " AND m.is_llm_role = TRUE"

    query += """
        GROUP BY m.is_senior

        ORDER BY number_of_jobs DESC
    """

    return run_query(query, params)

def get_remote_friendly_vs_non_remote(filters):

    query = """
        SELECT
            CASE
                WHEN m.is_remote_friendly = TRUE
                THEN 'Remote-Friendly'
                ELSE 'Non-Remote-Friendly'
            END AS remote_status,

            COUNT(*) AS number_of_jobs

        FROM jobs j

        LEFT JOIN job_market m
            ON m.job_id = j.job_id

        WHERE 1=1
    """

    params = []


    if filters["job_title"]:
        query += " AND j.job_title = ANY(%s)"
        params.append(filters["job_title"])

    if filters["experience"]:
        query += " AND j.experience_level = ANY(%s)"
        params.append(filters["experience"])

    if filters["industry"]:
        query += " AND c.industry = ANY(%s)"
        params.append(filters["industry"])

    if filters["category"]:
        query += " AND j.job_category = ANY(%s)"
        params.append(filters["category"])

    if filters["senior"]:
        query += " AND m.is_senior = TRUE"

    if filters["remote"]:
        query += " AND m.is_remote_friendly = TRUE"

    if filters["llm"]:
        query += " AND m.is_llm_role = TRUE"

    query += """
        GROUP BY m.is_remote_friendly

        ORDER BY number_of_jobs DESC
    """

    return run_query(query, params)