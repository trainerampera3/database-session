
SELECT DISTINCT year
FROM time_dim
ORDER BY year;



SELECT DISTINCT quarter
FROM time_dim
ORDER BY quarter;



SELECT DISTINCT month
FROM time_dim
ORDER BY month;



SELECT DISTINCT division
FROM store_dim
ORDER BY division;


SELECT DISTINCT district
FROM store_dim
ORDER BY district;



SELECT DISTINCT trans_type
FROM trans_dim
ORDER BY trans_type;



SELECT DISTINCT item_name
FROM item_dim
ORDER BY item_name;



SELECT COALESCE(SUM(f.total_price), 0) AS total_sales
FROM fact_table f
JOIN time_dim t
    ON f.time_key = t.time_key
JOIN store_dim s
    ON f.store_key = s.store_key
JOIN trans_dim p
    ON f.payment_key = p.payment_key
JOIN item_dim i
    ON f.item_key = i.item_key
WHERE 1 = 1;



SELECT COUNT(*) AS total_transactions
FROM fact_table f
JOIN time_dim t
    ON f.time_key = t.time_key
JOIN store_dim s
    ON f.store_key = s.store_key
JOIN trans_dim p
    ON f.payment_key = p.payment_key
JOIN item_dim i
    ON f.item_key = i.item_key
WHERE 1 = 1;



SELECT COALESCE(SUM(f.quantity), 0) AS total_quantity
FROM fact_table f
JOIN time_dim t
    ON f.time_key = t.time_key
JOIN store_dim s
    ON f.store_key = s.store_key
JOIN trans_dim p
    ON f.payment_key = p.payment_key
JOIN item_dim i
    ON f.item_key = i.item_key
WHERE 1 = 1;



SELECT COUNT(DISTINCT f.coustomer_key) AS unique_customers
FROM fact_table f
JOIN time_dim t
    ON f.time_key = t.time_key
JOIN store_dim s
    ON f.store_key = s.store_key
JOIN trans_dim p
    ON f.payment_key = p.payment_key
JOIN item_dim i
    ON f.item_key = i.item_key
WHERE 1 = 1;




SELECT
    t.year,
    SUM(f.total_price) AS total_sales
FROM fact_table f
JOIN time_dim t
    ON f.time_key = t.time_key
JOIN store_dim s
    ON f.store_key = s.store_key
JOIN trans_dim p
    ON f.payment_key = p.payment_key
JOIN item_dim i
    ON f.item_key = i.item_key
WHERE 1 = 1
GROUP BY t.year
ORDER BY t.year;




SELECT
    t.month,
    SUM(f.total_price) AS total_sales
FROM fact_table f
JOIN time_dim t
    ON f.time_key = t.time_key
JOIN store_dim s
    ON f.store_key = s.store_key
JOIN trans_dim p
    ON f.payment_key = p.payment_key
JOIN item_dim i
    ON f.item_key = i.item_key
WHERE 1 = 1
GROUP BY t.month
ORDER BY t.month;




SELECT
    p.trans_type,
    SUM(f.total_price) AS total_sales
FROM fact_table f
JOIN time_dim t
    ON f.time_key = t.time_key
JOIN store_dim s
    ON f.store_key = s.store_key
JOIN trans_dim p
    ON f.payment_key = p.payment_key
JOIN item_dim i
    ON f.item_key = i.item_key
WHERE 1 = 1
GROUP BY p.trans_type
ORDER BY total_sales DESC;




SELECT
    s.division,
    SUM(f.total_price) AS total_sales
FROM fact_table f
JOIN time_dim t
    ON f.time_key = t.time_key
JOIN store_dim s
    ON f.store_key = s.store_key
JOIN trans_dim p
    ON f.payment_key = p.payment_key
JOIN item_dim i
    ON f.item_key = i.item_key
WHERE 1 = 1
GROUP BY s.division
ORDER BY total_sales DESC;




SELECT
    i.item_name,
    SUM(f.total_price) AS total_sales
FROM fact_table f
JOIN time_dim t
    ON f.time_key = t.time_key
JOIN store_dim s
    ON f.store_key = s.store_key
JOIN trans_dim p
    ON f.payment_key = p.payment_key
JOIN item_dim i
    ON f.item_key = i.item_key
WHERE 1 = 1
GROUP BY i.item_name
ORDER BY total_sales DESC
LIMIT 10;



SELECT
    i.item_name,
    SUM(f.quantity) AS quantity
FROM fact_table f
JOIN time_dim t
    ON f.time_key = t.time_key
JOIN store_dim s
    ON f.store_key = s.store_key
JOIN trans_dim p
    ON f.payment_key = p.payment_key
JOIN item_dim i
    ON f.item_key = i.item_key
WHERE 1 = 1
GROUP BY i.item_name
ORDER BY quantity DESC
LIMIT 10;



SELECT
    s.district,
    SUM(f.total_price) AS total_sales
FROM fact_table f
JOIN time_dim t
    ON f.time_key = t.time_key
JOIN store_dim s
    ON f.store_key = s.store_key
JOIN trans_dim p
    ON f.payment_key = p.payment_key
JOIN item_dim i
    ON f.item_key = i.item_key
WHERE 1 = 1
GROUP BY s.district
ORDER BY total_sales DESC
LIMIT 10;


SELECT
    s.district,
    COUNT(*) AS transactions
FROM fact_table f
JOIN time_dim t
    ON f.time_key = t.time_key
JOIN store_dim s
    ON f.store_key = s.store_key
JOIN trans_dim p
    ON f.payment_key = p.payment_key
JOIN item_dim i
    ON f.item_key = i.item_key
WHERE 1 = 1
GROUP BY s.district
ORDER BY transactions DESC
LIMIT 10;