-- Executive KPI reconciliation
SELECT
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND(SUM(profit) / NULLIF(SUM(revenue), 0), 4) AS profit_margin,
    SUM(order_flag) AS orders,
    SUM(return_order_flag) AS returned_orders,
    ROUND(1.0 * SUM(return_order_flag) / NULLIF(SUM(order_flag), 0), 4) AS return_rate,
    ROUND(SUM(revenue) / NULLIF(SUM(order_flag), 0), 2) AS average_order_value
FROM fact_sales;

-- Monthly KPI trend with target attainment
SELECT
    f.year_month,
    ROUND(SUM(f.revenue), 2) AS revenue,
    ROUND(SUM(f.profit), 2) AS profit,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.revenue), 0), 4) AS profit_margin,
    SUM(f.order_flag) AS orders,
    SUM(f.return_order_flag) AS returned_orders,
    ROUND(1.0 * SUM(f.return_order_flag) / NULLIF(SUM(f.order_flag), 0), 4) AS return_rate,
    t.target_revenue,
    ROUND(SUM(f.revenue) / NULLIF(t.target_revenue, 0), 4) AS target_attainment
FROM fact_sales f
JOIN monthly_targets t ON f.year_month = t.year_month
GROUP BY f.year_month, t.target_revenue
ORDER BY f.year_month;

-- Year-over-year performance
SELECT
    d.year,
    ROUND(SUM(f.revenue), 2) AS revenue,
    ROUND(SUM(f.profit), 2) AS profit,
    SUM(f.order_flag) AS orders,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.revenue), 0), 4) AS profit_margin
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year
ORDER BY d.year;

