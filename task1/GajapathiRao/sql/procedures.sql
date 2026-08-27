

CREATE OR REPLACE PROCEDURE process_trans_batch(
    p_batch JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO trans_dim (
        payment_key,
        trans_type,
        bank_name
    )

    SELECT
        payment_key,
        trans_type,
        bank_name

    FROM jsonb_to_recordset(p_batch) AS records(
        payment_key VARCHAR(10),
        trans_type VARCHAR(20),
        bank_name VARCHAR(150)
    );

END;
$$;




CREATE OR REPLACE PROCEDURE process_customer_batch(
    p_batch JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO customer_dim (
        coustomer_key,
        name,
        contact_no,
        nid
    )

    SELECT
        coustomer_key,
        name,
        contact_no,
        nid

    FROM jsonb_to_recordset(p_batch) AS records(
        coustomer_key VARCHAR(20),
        name VARCHAR(100),
        contact_no BIGINT,
        nid BIGINT
    );

END;
$$;




CREATE OR REPLACE PROCEDURE process_item_batch(
    p_batch JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO item_dim (
        item_key,
        item_name,
        "desc",
        unit_price,
        man_country,
        supplier,
        unit
    )

    SELECT
        item_key,
        item_name,
        "desc",
        unit_price,
        man_country,
        supplier,
        unit

    FROM jsonb_to_recordset(p_batch) AS records(
        item_key VARCHAR(20),
        item_name VARCHAR(255),
        "desc" TEXT,
        unit_price NUMERIC(10,2),
        man_country VARCHAR(100),
        supplier VARCHAR(255),
        unit VARCHAR(50)
    );

END;
$$;




CREATE OR REPLACE PROCEDURE process_store_batch(
    p_batch JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO store_dim (
        store_key,
        division,
        district,
        upazila
    )

    SELECT
        store_key,
        division,
        district,
        upazila

    FROM jsonb_to_recordset(p_batch) AS records(
        store_key VARCHAR(20),
        division VARCHAR(100),
        district VARCHAR(100),
        upazila VARCHAR(100)
    );

END;
$$;



CREATE OR REPLACE PROCEDURE process_time_batch(
    p_batch JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO time_dim (
        time_key,
        date,
        hour,
        day,
        week,
        month,
        quarter,
        year
    )

    SELECT
        time_key,
        date,
        hour,
        day,
        week,
        month,
        quarter,
        year

    FROM jsonb_to_recordset(p_batch) AS records(
        time_key VARCHAR(20),
        date TIMESTAMP,
        hour INTEGER,
        day INTEGER,
        week VARCHAR(30),
        month INTEGER,
        quarter VARCHAR(10),
        year INTEGER
    );

END;
$$;




CREATE OR REPLACE PROCEDURE process_fact_batch(
    p_batch JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO fact_table (
        payment_key,
        coustomer_key,
        time_key,
        item_key,
        store_key,
        quantity,
        unit,
        unit_price,
        total_price
    )

    SELECT
        payment_key,
        coustomer_key,
        time_key,
        item_key,
        store_key,
        quantity,
        unit,
        unit_price,
        total_price

    FROM jsonb_to_recordset(p_batch) AS records(
        payment_key VARCHAR(10),
        coustomer_key VARCHAR(20),
        time_key VARCHAR(20),
        item_key VARCHAR(20),
        store_key VARCHAR(20),
        quantity INTEGER,
        unit VARCHAR(50),
        unit_price NUMERIC(10,2),
        total_price NUMERIC(12,2)
    );

END;
$$;