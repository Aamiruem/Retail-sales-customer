-- Return rate by category and channel
SELECT
    p.category,
    f.channel,
    SUM(f.order_flag) AS orders,
    SUM(f.return_order_flag) AS returned_orders,
    ROUND(1.0 * SUM(f.return_order_flag) / NULLIF(SUM(f.order_flag), 0), 4) AS return_rate,
    ROUND(SUM(f.return_amount), 2) AS return_value
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category, f.channel
ORDER BY return_rate DESC;

-- Discount-band profitability
WITH discount_bands AS (
    SELECT
        CASE
            WHEN discount_pct = 0 THEN 'No Discount'
            WHEN discount_pct <= 0.10 THEN '1-10%'
            WHEN discount_pct <= 0.20 THEN '11-20%'
            ELSE 'Above 20%'
        END AS discount_band,
        revenue,
        profit,
        order_flag
    FROM fact_sales
)
SELECT
    discount_band,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND(SUM(profit) / NULLIF(SUM(revenue), 0), 4) AS profit_margin,
    SUM(order_flag) AS orders
FROM discount_bands
GROUP BY discount_band
ORDER BY CASE discount_band
    WHEN 'No Discount' THEN 1
    WHEN '1-10%' THEN 2
    WHEN '11-20%' THEN 3
    ELSE 4
END;

-- Monthly target attainment and variance
SELECT
    f.year_month,
    ROUND(SUM(f.revenue), 2) AS actual_revenue,
    t.target_revenue,
    ROUND(SUM(f.revenue) - t.target_revenue, 2) AS variance,
    ROUND(SUM(f.revenue) / NULLIF(t.target_revenue, 0), 4) AS attainment
FROM fact_sales f
JOIN monthly_targets t ON f.year_month = t.year_month
GROUP BY f.year_month, t.target_revenue
ORDER BY f.year_month;

