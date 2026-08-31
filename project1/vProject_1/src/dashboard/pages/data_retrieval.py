import pandas as pd


def _fetch_dataframe(connection, query, params=None):
    """execute a query and return the result as a dataframe."""
    with connection.cursor() as cursor:
        cursor.execute(
            query,
            params or ()
        )

        rows = cursor.fetchall()

        columns = [
            description.name
            for description in cursor.description
        ]

    return pd.DataFrame(
        rows,
        columns=columns
    )


def get_market_kpis(connection):
    """return high-level business-location kpis."""
    query = """
        SELECT
            (
                SELECT COUNT(*)
                FROM business_location.companies
            ) AS total_companies,

            (
                SELECT COUNT(*)
                FROM business_location.companies
                WHERE UPPER(company_status) IN ('ACTV', 'ACTIVE')
            ) AS active_companies,

            (
                SELECT COUNT(DISTINCT city)
                FROM business_location.startup_funding
                WHERE city IS NOT NULL
                  AND TRIM(city) <> ''
            ) AS startup_cities,

            (
                SELECT COALESCE(
                    SUM(funding_amount),
                    0
                )
                FROM business_location.startup_funding
            ) AS total_funding,

            (
                SELECT COUNT(DISTINCT registered_state)
                FROM business_location.companies
                WHERE registered_state IS NOT NULL
            ) AS company_states,

            (
                SELECT COUNT(DISTINCT state)
                FROM business_location.state_policies
                WHERE state IS NOT NULL
            ) AS policy_states
    """

    return _fetch_dataframe(
        connection,
        query
    )


def get_companies_by_state(connection):
    """return registered companies by state."""
    query = """
        SELECT
            registered_state AS state,
            COUNT(*) AS company_count

        FROM business_location.companies

        WHERE registered_state IS NOT NULL
          AND TRIM(registered_state) <> ''

        GROUP BY registered_state

        ORDER BY company_count DESC
    """

    return _fetch_dataframe(
        connection,
        query
    )


def get_company_registration_trend(connection):
    """return company registrations grouped by year."""
    query = """
        SELECT
            EXTRACT(
                YEAR FROM registration_date
            )::INTEGER AS year,

            COUNT(*) AS company_count

        FROM business_location.companies

        WHERE registration_date IS NOT NULL

        GROUP BY year

        ORDER BY year
    """

    return _fetch_dataframe(
        connection,
        query
    )


def get_office_market_by_city(connection):
    """return aggregated office-market information by city."""
    query = """
        SELECT
            city,
            state,

            ROUND(
                AVG(rent_per_sqft)::NUMERIC,
                2
            ) AS avg_rent_per_sqft,

            ROUND(
                AVG(vacancy_rate)::NUMERIC,
                2
            ) AS avg_vacancy_rate,

            COUNT(*) AS market_records

        FROM business_location.office_market

        WHERE city IS NOT NULL
          AND TRIM(city) <> ''

        GROUP BY city, state

        ORDER BY avg_rent_per_sqft
    """

    return _fetch_dataframe(
        connection,
        query
    )


def get_city_office_market(connection, city):
    """return detailed office-market records for a city."""
    query = """
        SELECT
            city,
            state,
            locality,
            property_type,
            rent_per_sqft,
            rent_per_sqm,
            vacancy_rate,
            availability,
            market_date

        FROM business_location.office_market

        WHERE LOWER(city) = LOWER(%s)

        ORDER BY market_date DESC NULLS LAST
    """

    return _fetch_dataframe(
        connection,
        query,
        (city,)
    )


def get_startup_funding_by_city(connection):
    """return startup funding aggregated by city."""
    query = """
        SELECT
            city,
            state,

            COUNT(DISTINCT startup_name)
                AS startup_count,

            COALESCE(
                SUM(funding_amount),
                0
            ) AS total_funding

        FROM business_location.startup_funding

        WHERE city IS NOT NULL
          AND TRIM(city) <> ''

        GROUP BY city, state

        ORDER BY total_funding DESC
    """

    return _fetch_dataframe(
        connection,
        query
    )


def get_funding_by_sector(connection):
    """return startup funding aggregated by sector."""
    query = """
        SELECT
            sector,

            COUNT(DISTINCT startup_name)
                AS startup_count,

            COALESCE(
                SUM(funding_amount),
                0
            ) AS total_funding

        FROM business_location.startup_funding

        WHERE sector IS NOT NULL
          AND TRIM(sector) <> ''

        GROUP BY sector

        ORDER BY total_funding DESC
    """

    return _fetch_dataframe(
        connection,
        query
    )


def get_funding_by_stage(connection):
    """return startup funding aggregated by funding stage."""
    query = """
        SELECT
            funding_stage,

            COUNT(*) AS funding_records,

            COALESCE(
                SUM(funding_amount),
                0
            ) AS total_funding

        FROM business_location.startup_funding

        WHERE funding_stage IS NOT NULL
          AND TRIM(funding_stage) <> ''

        GROUP BY funding_stage

        ORDER BY total_funding DESC
    """

    return _fetch_dataframe(
        connection,
        query
    )


def get_city_startup_funding(connection, city):
    """return detailed startup funding records for a city."""
    query = """
        SELECT
            city,
            state,
            startup_name,
            sector,
            funding_stage,
            funding_amount,
            funding_date,
            investor_name

        FROM business_location.startup_funding

        WHERE LOWER(city) = LOWER(%s)

        ORDER BY funding_date DESC NULLS LAST
    """

    return _fetch_dataframe(
        connection,
        query,
        (city,)
    )


def get_company_status_distribution(connection):
    """return company count by company status."""
    query = """
        SELECT
            company_status,
            COUNT(*) AS company_count

        FROM business_location.companies

        WHERE company_status IS NOT NULL

        GROUP BY company_status

        ORDER BY company_count DESC
    """

    return _fetch_dataframe(
        connection,
        query
    )


def get_company_industry_distribution(connection):
    """return company count by industrial classification."""
    query = """
        SELECT
            industrial_class,
            COUNT(*) AS company_count

        FROM business_location.companies

        WHERE industrial_class IS NOT NULL
          AND TRIM(industrial_class) <> ''

        GROUP BY industrial_class

        ORDER BY company_count DESC

        LIMIT 15
    """

    return _fetch_dataframe(
        connection,
        query
    )


def get_company_capital_profile(connection):
    """return aggregate company capital information."""
    query = """
        SELECT
            ROUND(
                AVG(authorized_cap)::NUMERIC,
                2
            ) AS avg_authorized_capital,

            ROUND(
                AVG(paidup_capital)::NUMERIC,
                2
            ) AS avg_paidup_capital,

            COALESCE(
                SUM(authorized_cap),
                0
            ) AS total_authorized_capital,

            COALESCE(
                SUM(paidup_capital),
                0
            ) AS total_paidup_capital

        FROM business_location.companies
    """

    return _fetch_dataframe(
        connection,
        query
    )


def get_city_company_summary(connection, state=None):
    """return company ecosystem summary by state."""
    if state:
        query = """
            SELECT
                registered_state AS state,

                COUNT(*) AS total_companies,

                COUNT(*) FILTER (
                    WHERE UPPER(company_status)
                    IN ('ACTIVE', 'ACTV')
                ) AS active_companies,

                ROUND(
                    AVG(paidup_capital)::NUMERIC,
                    2
                ) AS avg_paidup_capital

            FROM business_location.companies

            WHERE LOWER(registered_state)
                  = LOWER(%s)

            GROUP BY registered_state

            ORDER BY total_companies DESC
        """

        return _fetch_dataframe(
            connection,
            query,
            (state,)
        )

    query = """
        SELECT
            registered_state AS state,

            COUNT(*) AS total_companies,

            COUNT(*) FILTER (
                WHERE UPPER(company_status)
                IN ('ACTIVE', 'ACTV')
            ) AS active_companies,

            ROUND(
                AVG(paidup_capital)::NUMERIC,
                2
            ) AS avg_paidup_capital

        FROM business_location.companies

        WHERE registered_state IS NOT NULL

        GROUP BY registered_state

        ORDER BY total_companies DESC
    """

    return _fetch_dataframe(
        connection,
        query
    )


def get_policy_summary(connection):
    """return overall government-policy summary."""
    query = """
        SELECT
            COUNT(*) AS total_policies,

            COUNT(DISTINCT state)
                AS states_covered,

            COUNT(DISTINCT sector)
                AS sectors_covered,

            COUNT(DISTINCT incentive_type)
                AS incentive_types

        FROM business_location.state_policies
    """

    return _fetch_dataframe(
        connection,
        query
    )


def get_policies_by_state(connection):
    """return number of policies available by state."""
    query = """
        SELECT
            state,
            COUNT(*) AS policy_count

        FROM business_location.state_policies

        WHERE state IS NOT NULL
          AND TRIM(state) <> ''

        GROUP BY state

        ORDER BY policy_count DESC
    """

    return _fetch_dataframe(
        connection,
        query
    )


def get_state_policies(connection, state):
    """return policies for a selected state."""
    query = """
        SELECT
            state,
            policy_name,
            sector,
            incentive_type,
            incentive_description,
            eligibility,
            benefit,
            effective_from,
            effective_to

        FROM business_location.state_policies

        WHERE LOWER(state) = LOWER(%s)

        ORDER BY effective_from DESC NULLS LAST
    """

    return _fetch_dataframe(
        connection,
        query,
        (state,)
    )


def get_states(connection):
    """return states available across the project datasets."""
    query = """
        SELECT DISTINCT state

        FROM (
            SELECT registered_state AS state
            FROM business_location.companies

            UNION

            SELECT state
            FROM business_location.office_market

            UNION

            SELECT state
            FROM business_location.startup_funding

            UNION

            SELECT state
            FROM business_location.state_policies
        ) AS states

        WHERE state IS NOT NULL
          AND TRIM(state) <> ''

        ORDER BY state
    """

    return _fetch_dataframe(
        connection,
        query
    )


def get_cities(connection, state=None):
    """return cities from office-market and startup datasets."""
    if state:
        query = """
            SELECT DISTINCT city

            FROM (
                SELECT city, state
                FROM business_location.office_market

                UNION

                SELECT city, state
                FROM business_location.startup_funding
            ) AS cities

            WHERE city IS NOT NULL
              AND TRIM(city) <> ''

              AND LOWER(state)
                  = LOWER(%s)

            ORDER BY city
        """

        return _fetch_dataframe(
            connection,
            query,
            (state,)
        )

    query = """
        SELECT DISTINCT city

        FROM (
            SELECT city
            FROM business_location.office_market

            UNION

            SELECT city
            FROM business_location.startup_funding
        ) AS cities

        WHERE city IS NOT NULL
          AND TRIM(city) <> ''

        ORDER BY city
    """

    return _fetch_dataframe(
        connection,
        query
    )


def get_city_profile(connection, city):
    """return measurable indicators for a selected city."""
    company_query = """
        SELECT
            COUNT(*) AS total_companies,

            COUNT(*) FILTER (
                WHERE UPPER(company_status)
                IN ('ACTIVE', 'ACTV')
            ) AS active_companies

        FROM business_location.companies

        WHERE LOWER(
            registered_office_address
        ) LIKE LOWER(%s)
    """

    office_query = """
        SELECT
            ROUND(
                AVG(rent_per_sqft)::NUMERIC,
                2
            ) AS avg_rent_per_sqft,

            ROUND(
                AVG(vacancy_rate)::NUMERIC,
                2
            ) AS avg_vacancy_rate

        FROM business_location.office_market

        WHERE LOWER(city) = LOWER(%s)
    """

    startup_query = """
        SELECT
            COUNT(DISTINCT startup_name)
                AS startup_count,

            COALESCE(
                SUM(funding_amount),
                0
            ) AS total_funding

        FROM business_location.startup_funding

        WHERE LOWER(city) = LOWER(%s)
    """

    policy_query = """
        SELECT
            COUNT(*) AS policy_count

        FROM business_location.state_policies p

        WHERE EXISTS (
            SELECT 1

            FROM business_location.office_market o

            WHERE LOWER(o.city) = LOWER(%s)
              AND LOWER(o.state) = LOWER(p.state)
        )
    """

    company_df = _fetch_dataframe(
        connection,
        company_query,
        (f"%{city}%",)
    )

    office_df = _fetch_dataframe(
        connection,
        office_query,
        (city,)
    )

    startup_df = _fetch_dataframe(
        connection,
        startup_query,
        (city,)
    )

    policy_df = _fetch_dataframe(
        connection,
        policy_query,
        (city,)
    )

    return {
        "companies": company_df,
        "office": office_df,
        "startup": startup_df,
        "policies": policy_df
    }


def get_requirement_sectors(connection):
    """return normalized business sectors available to the user."""
    query = """
        SELECT sector
        FROM (
            SELECT DISTINCT
                CASE
                    WHEN LOWER(TRIM(sector)) IN (
                        'it',
                        'technology',
                        'software / it',
                        'software',
                        'information technology'
                    )
                        THEN 'IT / Software'

                    WHEN LOWER(TRIM(sector)) IN (
                        'finance',
                        'fintech'
                    )
                        THEN 'Finance'

                    WHEN LOWER(TRIM(sector)) IN (
                        'healthcare',
                        'health tech',
                        'healthtech'
                    )
                        THEN 'Healthcare'

                    WHEN LOWER(TRIM(sector)) IN (
                        'e-commerce',
                        'ecommerce',
                        'consumer internet'
                    )
                        THEN 'E-Commerce'

                    WHEN LOWER(TRIM(sector)) IN (
                        'manufacturing',
                        'automotive',
                        'industrial'
                    )
                        THEN 'Manufacturing'

                    ELSE TRIM(sector)
                END AS sector

            FROM business_location.startup_funding

            UNION

            SELECT DISTINCT
                CASE
                    WHEN LOWER(TRIM(sector)) IN (
                        'it',
                        'technology',
                        'software / it',
                        'software',
                        'information technology'
                    )
                        THEN 'IT / Software'

                    WHEN LOWER(TRIM(sector)) IN (
                        'finance',
                        'fintech'
                    )
                        THEN 'Finance'

                    WHEN LOWER(TRIM(sector)) IN (
                        'healthcare',
                        'health tech',
                        'healthtech'
                    )
                        THEN 'Healthcare'

                    WHEN LOWER(TRIM(sector)) IN (
                        'e-commerce',
                        'ecommerce',
                        'consumer internet'
                    )
                        THEN 'E-Commerce'

                    WHEN LOWER(TRIM(sector)) IN (
                        'manufacturing',
                        'automotive',
                        'industrial'
                    )
                        THEN 'Manufacturing'

                    ELSE TRIM(sector)
                END AS sector

            FROM business_location.state_policies
        ) AS normalized_sectors

        WHERE sector IS NOT NULL
          AND TRIM(sector) <> ''

        ORDER BY sector
    """

    return _fetch_dataframe(
        connection,
        query
    )


def get_requirement_location_analysis(
    connection,
    sector="Any",
    company_size="Any",
    office_requirement="Any"
):
    """
    return city-level location results based on the selected
    business requirements.

    company size:
        small  -> paid-up capital < 10 lakh
        medium -> 10 lakh to < 1 crore
        large  -> >= 1 crore

    office requirement:
        budget   -> rent < 100
        standard -> 100 to < 200
        premium  -> >= 200
    """
    params = []

    # apply the selected office requirement
    office_condition = ""

    if office_requirement == "Budget":
        office_condition = """
            AND rent_per_sqft < 100
        """

    elif office_requirement == "Standard":
        office_condition = """
            AND rent_per_sqft >= 100
            AND rent_per_sqft < 200
        """

    elif office_requirement == "Premium":
        office_condition = """
            AND rent_per_sqft >= 200
        """

    # apply the selected company size
    company_condition = ""

    if company_size == "Small":
        company_condition = """
            AND COALESCE(c.paidup_capital, 0) < 1000000
        """

    elif company_size == "Medium":
        company_condition = """
            AND COALESCE(c.paidup_capital, 0) >= 1000000
            AND COALESCE(c.paidup_capital, 0) < 10000000
        """

    elif company_size == "Large":
        company_condition = """
            AND COALESCE(c.paidup_capital, 0) >= 10000000
        """

    # apply the selected startup sector
    sector_condition = ""

    if sector and sector != "Any":
        sector_condition = """
            AND CASE
                WHEN LOWER(TRIM(sf.sector)) IN (
                    'it',
                    'technology',
                    'software / it',
                    'software',
                    'information technology'
                )
                    THEN 'IT / Software'

                WHEN LOWER(TRIM(sf.sector)) IN (
                    'finance',
                    'fintech'
                )
                    THEN 'Finance'

                WHEN LOWER(TRIM(sf.sector)) IN (
                    'healthcare',
                    'health tech',
                    'healthtech'
                )
                    THEN 'Healthcare'

                WHEN LOWER(TRIM(sf.sector)) IN (
                    'e-commerce',
                    'ecommerce',
                    'consumer internet'
                )
                    THEN 'E-Commerce'

                WHEN LOWER(TRIM(sf.sector)) IN (
                    'manufacturing',
                    'automotive',
                    'industrial'
                )
                    THEN 'Manufacturing'

                ELSE TRIM(sf.sector)
            END = %s
        """

        params.append(sector)

    query = f"""
        WITH office_data AS (
            SELECT
                city,
                state,

                ROUND(
                    AVG(rent_per_sqft)::NUMERIC,
                    2
                ) AS avg_office_cost,

                ROUND(
                    AVG(vacancy_rate)::NUMERIC,
                    2
                ) AS avg_vacancy_rate

            FROM business_location.office_market

            WHERE city IS NOT NULL
              AND TRIM(city) <> ''

              {office_condition}

            GROUP BY city, state
        ),

        company_data AS (
            SELECT
                o.city,
                o.state,
                COUNT(*) AS company_count

            FROM office_data o

            JOIN business_location.companies c
                ON LOWER(
                    c.registered_office_address
                ) LIKE LOWER(
                    '%%' || o.city || '%%'
                )

            WHERE c.registered_office_address IS NOT NULL

                {company_condition}

            GROUP BY
                o.city,
                o.state
        ),

        funding_data AS (
            SELECT
                sf.city,
                sf.state,

                COUNT(
                    DISTINCT sf.startup_name
                ) AS startup_count,

                COALESCE(
                    SUM(sf.funding_amount),
                    0
                ) AS total_funding

            FROM business_location.startup_funding sf

            WHERE sf.city IS NOT NULL
              AND TRIM(sf.city) <> ''

              {sector_condition}

            GROUP BY
                sf.city,
                sf.state
        ),

        policy_data AS (
            SELECT
                state,
                COUNT(*) AS incentive_count

            FROM business_location.state_policies

            WHERE state IS NOT NULL
              AND TRIM(state) <> ''

            GROUP BY state
        )

        SELECT
            o.city AS city,
            o.state AS state,

            o.avg_office_cost AS avg_office_cost,
            o.avg_vacancy_rate AS avg_vacancy_rate,

            COALESCE(
                c.company_count,
                0
            ) AS company_count,

            COALESCE(
                f.startup_count,
                0
            ) AS startup_count,

            COALESCE(
                f.total_funding,
                0
            ) AS total_funding,

            COALESCE(
                p.incentive_count,
                0
            ) AS incentive_count

        FROM office_data o

        LEFT JOIN company_data c
            ON LOWER(c.city) = LOWER(o.city)
           AND LOWER(c.state) = LOWER(o.state)

        LEFT JOIN funding_data f
            ON LOWER(f.city) = LOWER(o.city)
           AND LOWER(f.state) = LOWER(o.state)

        LEFT JOIN policy_data p
            ON LOWER(p.state) = LOWER(o.state)

        ORDER BY
            company_count DESC,
            total_funding DESC,
            incentive_count DESC

        LIMIT 15
    """

    return _fetch_dataframe(
        connection,
        query,
        tuple(params)
    )

