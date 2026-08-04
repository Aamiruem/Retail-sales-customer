-- Category performance and profitability
SELECT
    p.category,
    ROUND(SUM(f.revenue), 2) AS revenue,
    ROUND(SUM(f.profit), 2) AS profit,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.revenue), 0), 4) AS profit_margin,
    SUM(f.order_flag) AS allocated_orders,
    SUM(f.return_order_flag) AS returned_orders,
    ROUND(1.0 * SUM(f.return_order_flag) / NULLIF(SUM(f.order_flag), 0), 4) AS return_rate
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY revenue DESC;

-- Top products by revenue
SELECT
    p.product_id,
    p.product_name,
    p.category,
    ROUND(SUM(f.revenue), 2) AS revenue,
    ROUND(SUM(f.profit), 2) AS profit,
    SUM(f.quantity) AS units,
    SUM(f.return_flag) AS returned_lines
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_id, p.product_name, p.category
ORDER BY revenue DESC
LIMIT 15;

-- Regional category matrix
SELECT
    c.region,
    p.category,
    ROUND(SUM(f.revenue), 2) AS revenue,
    ROUND(SUM(f.profit), 2) AS profit
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY c.region, p.category
ORDER BY c.region, revenue DESC;

