CREATE TABLE IF NOT EXISTS trans_dim (
    payment_key VARCHAR(10) PRIMARY KEY,
    trans_type VARCHAR(20),
    bank_name VARCHAR(150)
);

CREATE TABLE IF NOT EXISTS customer_dim (
    coustomer_key VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    contact_no BIGINT,
    nid BIGINT
);

CREATE TABLE IF NOT EXISTS item_dim (
    item_key VARCHAR(20) PRIMARY KEY,
    item_name VARCHAR(255),
    "desc" TEXT,
    unit_price NUMERIC(10, 2),
    man_country VARCHAR(100),
    supplier VARCHAR(255),
    unit VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS store_dim (
    store_key VARCHAR(20) PRIMARY KEY,
    division VARCHAR(100),
    district VARCHAR(100),
    upazila VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS time_dim (
    time_key VARCHAR(20) PRIMARY KEY,
    date TIMESTAMP,
    hour INTEGER,
    day INTEGER,
    week VARCHAR(30),
    month INTEGER,
    quarter VARCHAR(10),
    year INTEGER
);

CREATE TABLE IF NOT EXISTS fact_table (
    payment_key VARCHAR(10),
    coustomer_key VARCHAR(20),
    time_key VARCHAR(20),
    item_key VARCHAR(20),
    store_key VARCHAR(20),
    quantity INTEGER,
    unit VARCHAR(50),
    unit_price NUMERIC(10, 2),
    total_price NUMERIC(12, 2),

    FOREIGN KEY (payment_key)
        REFERENCES trans_dim(payment_key),

    FOREIGN KEY (coustomer_key)
        REFERENCES customer_dim(coustomer_key),

    FOREIGN KEY (time_key)
        REFERENCES time_dim(time_key),

    FOREIGN KEY (item_key)
        REFERENCES item_dim(item_key),

    FOREIGN KEY (store_key)
        REFERENCES store_dim(store_key)
);