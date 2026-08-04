-- RFM segment scorecard
SELECT
    rfm_segment,
    COUNT(*) AS customers,
    ROUND(SUM(monetary), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND(AVG(recency_days), 1) AS average_recency_days,
    ROUND(AVG(frequency), 2) AS average_orders
FROM customer_rfm
GROUP BY rfm_segment
ORDER BY customers DESC;

-- Top valuable customers
SELECT
    customer_id,
    customer_name,
    customer_segment,
    rfm_segment,
    recency_days,
    frequency,
    ROUND(monetary, 2) AS revenue,
    ROUND(profit, 2) AS profit
FROM customer_rfm
ORDER BY monetary DESC
LIMIT 20;

-- At-risk high-value customers for retention action
SELECT
    customer_id,
    customer_name,
    recency_days,
    frequency,
    ROUND(monetary, 2) AS lifetime_revenue,
    returned_orders
FROM customer_rfm
WHERE rfm_segment = 'At Risk'
ORDER BY monetary DESC
LIMIT 25;

