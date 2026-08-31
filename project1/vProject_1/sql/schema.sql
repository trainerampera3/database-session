CREATE SCHEMA IF NOT EXISTS business_location;

CREATE TABLE IF NOT EXISTS business_location.companies (
    company_id BIGSERIAL PRIMARY KEY,
    corporate_identification_number TEXT,
    company_name TEXT,
    company_status TEXT,
    company_class TEXT,
    company_category TEXT,
    company_sub_category TEXT,
    registration_date DATE,
    registered_state TEXT,
    authorized_cap NUMERIC,
    paidup_capital NUMERIC,
    industrial_class TEXT,
    business_activity TEXT,
    registered_office_address TEXT,
    registrar_of_companies TEXT,
    email_addr TEXT,
    latest_year_annual_return INTEGER,
    latest_year_financial_statement INTEGER
);

CREATE TABLE IF NOT EXISTS business_location.startup_funding (
    funding_id BIGSERIAL PRIMARY KEY,
    startup_name TEXT,
    city TEXT,
    state TEXT,
    sector TEXT,
    funding_stage TEXT,
    funding_amount NUMERIC,
    funding_date DATE,
    investor_name TEXT,
    source TEXT
);

CREATE TABLE IF NOT EXISTS business_location.state_policies (
    policy_id BIGSERIAL PRIMARY KEY,
    state TEXT,
    policy_name TEXT,
    sector TEXT,
    incentive_type TEXT,
    incentive_description TEXT,
    eligibility TEXT,
    benefit TEXT,
    effective_from DATE,
    effective_to DATE,
    source TEXT
);

CREATE TABLE IF NOT EXISTS business_location.office_market (
    office_id BIGSERIAL PRIMARY KEY,
    city TEXT,
    state TEXT,
    locality TEXT,
    property_type TEXT,
    rent_per_sqft NUMERIC,
    rent_per_sqm NUMERIC,
    vacancy_rate NUMERIC,
    availability TEXT,
    market_date DATE,
    source TEXT
);

CREATE SCHEMA IF NOT EXISTS business_location;

CREATE TABLE IF NOT EXISTS business_location.batch_log (
    id BIGSERIAL PRIMARY KEY,
    batch_number VARCHAR(50) NOT NULL,
    source_file VARCHAR(255) NOT NULL,
    target_table VARCHAR(100) NOT NULL,
    stage VARCHAR(50) NOT NULL,
    rows_processed INTEGER NOT NULL DEFAULT 0,
    rows_inserted INTEGER NOT NULL DEFAULT 0,
    rows_rejected INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP NOT NULL,
    duration_seconds NUMERIC(12,4) NOT NULL DEFAULT 0,
    status VARCHAR(50) NOT NULL,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_companies_state
ON business_location.companies(registered_state);

CREATE INDEX IF NOT EXISTS idx_companies_registration_date
ON business_location.companies(registration_date);

CREATE INDEX IF NOT EXISTS idx_funding_state
ON business_location.startup_funding(state);

CREATE INDEX IF NOT EXISTS idx_funding_city
ON business_location.startup_funding(city);

CREATE INDEX IF NOT EXISTS idx_policy_state
ON business_location.state_policies(state);

CREATE INDEX IF NOT EXISTS idx_office_city
ON business_location.office_market(city);

CREATE INDEX IF NOT EXISTS idx_office_state
ON business_location.office_market(state);

CREATE INDEX IF NOT EXISTS idx_batch_log_source
ON business_location.batch_log(source_file);


-- To prevent duplicancey.

CREATE UNIQUE INDEX IF NOT EXISTS uq_companies_cin
ON business_location.companies(corporate_identification_number)
WHERE corporate_identification_number IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_startup_funding_key
ON business_location.startup_funding(
    startup_name,
    funding_date,
    funding_amount,
    city
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_state_policy_key
ON business_location.state_policies(
    state,
    policy_name,
    sector
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_office_market_key
ON business_location.office_market(
    city,
    state,
    locality,
    property_type,
    market_date
);