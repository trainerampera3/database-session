CREATE TABLE IF NOT EXISTS jobs (
    job_id VARCHAR(10) PRIMARY KEY,
    job_title VARCHAR(30),
    job_category VARCHAR(20),
    experience_level VARCHAR(10),
    years_of_experience INTEGER,
    education_required VARCHAR(40),
    required_skills TEXT
);


CREATE TABLE IF NOT EXISTS companies (
    company_id SERIAL PRIMARY KEY,
    job_id VARCHAR(10) NOT NULL,
    company_size VARCHAR(30),
    industry VARCHAR(20),

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
);


CREATE TABLE IF NOT EXISTS locations (
    location_id SERIAL PRIMARY KEY,
    job_id VARCHAR(10) NOT NULL,
    city VARCHAR(20),
    country VARCHAR(20),
    remote_work VARCHAR(20),

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
);


CREATE TABLE IF NOT EXISTS salaries (
    salary_id SERIAL PRIMARY KEY,
    job_id VARCHAR(10) NOT NULL,
    annual_salary_usd NUMERIC,
    salary_min_usd NUMERIC,
    salary_max_usd NUMERIC,
    ai_salary_premium_pct NUMERIC,

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
);


CREATE TABLE IF NOT EXISTS job_market (
    market_id SERIAL PRIMARY KEY,
    job_id VARCHAR(10) NOT NULL,
    demand_score INTEGER,
    demand_growth_yoy_pct NUMERIC,
    benefits_score_10 NUMERIC,
    posting_year INTEGER,
    posting_month INTEGER,
    is_senior BOOLEAN,
    is_remote_friendly BOOLEAN,
    is_llm_role BOOLEAN,

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
);