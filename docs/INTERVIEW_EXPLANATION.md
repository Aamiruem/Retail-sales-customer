# Interview Explanation

## 60-Second Project Answer

“My major data analytics project is a Retail Sales and Customer Insights Dashboard. I generated and integrated 4,224 synthetic retail records from CSV, Excel and SQLite. I built a Python ETL pipeline to handle duplicates, missing identifiers, invalid dates, incorrect quantities, discount errors and broken product keys, which produced 4,180 validated order lines. Then I designed a SQLite star schema and wrote SQL for KPIs, category, region, channel, RFM, discount, return and target analysis. The model reconciles to ₹160.1 million revenue, ₹41.3 million profit, a 25.8% margin, 3,922 orders and an 8.8% return rate. I delivered the analysis through a formula-driven Excel dashboard, a Power BI build kit with Power Query and DAX, and an interactive Streamlit app. I also added a data dictionary, reproducible notebook and automated quality tests.”

## Technical Questions

**Why a star schema?**  
It keeps measures in one fact table, descriptions in dimensions and relationships one-to-many. This reduces duplication, improves BI filtering and makes KPI logic consistent.

**How did you prevent order double counting?**  
Some orders contain two lines. I created `order_flag` and `return_order_flag`, equal to one only on the first line of each order. Summing these flags gives correct additive order metrics.

**How was RFM calculated?**  
Recency is days since the customer’s latest order, Frequency is distinct orders and Monetary is total revenue. Each measure is scored into quintiles, then business rules assign segments such as Champions, Loyal Customers, At Risk and Hibernating.

**How did you validate the project?**  
I used 15 automated checks for row counts, uniqueness, completeness, dates, ranges, foreign keys and arithmetic. I also reconciled headline KPIs independently through pandas, SQLite, Excel formulas and DAX validation queries.

**What business insight stood out?**  
Electronics drove the most revenue, but deep discounts reduced margin sharply. Beauty & Personal Care had high margin and the highest return rate, while At-Risk customers still represented meaningful revenue, creating a retention opportunity.

