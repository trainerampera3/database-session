CREATE TABLE jobs (
    job_id TEXT PRIMARY KEY,
    job_title TEXT,
    job_category TEXT,
    experience_level TEXT,
    years_of_experience INTEGER,
    education_required TEXT,
    required_skills TEXT
);

CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    job_id TEXT NOT NULL,
    company_size TEXT,
    industry TEXT,

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
);

CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    job_id TEXT NOT NULL,
    city TEXT,
    country TEXT,
    remote_work TEXT,

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
);

CREATE TABLE salaries (
    salary_id SERIAL PRIMARY KEY,
    job_id TEXT NOT NULL,
    annual_salary_usd NUMERIC,
    salary_min_usd NUMERIC,
    salary_max_usd NUMERIC,
    ai_salary_premium_pct NUMERIC,
    salary_tier TEXT,

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
);

CREATE TABLE job_market (
    market_id SERIAL PRIMARY KEY,
    job_id TEXT NOT NULL,
    demand_score INTEGER,
    demand_growth_yoy_pct NUMERIC,
    benefits_score_10 NUMERIC,
    posting_year INTEGER,
    posting_month INTEGER,
    is_senior INTEGER,
    is_remote_friendly INTEGER,
    is_llm_role INTEGER,

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
);