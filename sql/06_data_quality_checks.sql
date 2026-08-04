-- Fact grain and key uniqueness
SELECT
    COUNT(*) AS fact_rows,
    COUNT(DISTINCT line_id) AS unique_line_ids,
    COUNT(DISTINCT order_id) AS distinct_orders
FROM fact_sales;

-- Referential integrity checks: each result must be zero
SELECT 'missing_date' AS issue, COUNT(*) AS affected_rows
FROM fact_sales f LEFT JOIN dim_date d ON f.date_key = d.date_key
WHERE d.date_key IS NULL
UNION ALL
SELECT 'missing_customer', COUNT(*)
FROM fact_sales f LEFT JOIN dim_customer c ON f.customer_key = c.customer_key
WHERE c.customer_key IS NULL
UNION ALL
SELECT 'missing_product', COUNT(*)
FROM fact_sales f LEFT JOIN dim_product p ON f.product_key = p.product_key
WHERE p.product_key IS NULL
UNION ALL
SELECT 'missing_store', COUNT(*)
FROM fact_sales f LEFT JOIN dim_store s ON f.store_key = s.store_key
WHERE s.store_key IS NULL;

-- Arithmetic reconciliation: each maximum difference must be zero
SELECT
    ROUND(MAX(ABS(sales_after_discount - return_amount - revenue)), 2) AS max_revenue_difference,
    ROUND(MAX(ABS(revenue - cost_amount - profit)), 2) AS max_profit_difference
FROM fact_sales;

-- Join explosion guardrail
SELECT
    (SELECT COUNT(*) FROM fact_sales) AS fact_rows,
    (SELECT COUNT(*) FROM vw_sales_enriched) AS enriched_view_rows;

