# Power BI Report Page Plan

## Page 1 — Executive Overview

- Slicers: Year, Month, Region, Customer Segment, Channel.
- KPI cards: Revenue, Profit, Profit Margin, Orders, Return Rate, Target Attainment.
- Line chart: Revenue and Profit by Year Month.
- Clustered column + line: Actual Revenue versus Revenue Target.
- Bar chart: Revenue by Category.
- Bar chart: Revenue by Channel.
- Footer: dataset date range, 4,180 validated lines, synthetic-data label.

## Page 2 — Sales Performance

- KPI cards: Gross Sales, Discount Amount, Revenue, Profit, Average Order Value.
- Line chart: Revenue with previous-year comparator.
- Matrix: Region × Category with Revenue, Profit and Margin.
- Ranked bar: Top 10 Products by Revenue.
- Waterfall: Gross Sales → Discount → Returns → Revenue → Cost → Profit.
- Slicers: Date, Region, Category, Channel.

## Page 3 — Customer Insights & RFM

- KPI cards: Customers, Revenue per Customer, Champion Revenue, At-Risk Revenue.
- Bar chart: Customers by RFM Segment.
- Scatter: Frequency versus Monetary; size by Revenue; color by RFM Segment.
- Table: Top customers with Recency, Frequency, Monetary and Segment.
- Drill-through page tooltip: customer order history.

## Page 4 — Products, Discounts & Returns

- KPI cards: Returned Orders, Return Rate, Return Value, Weighted Average Discount.
- Bar chart: Return Rate by Category.
- Bar chart: Profit Margin by Discount Band.
- Scatter: Discount Rate versus Profit at order-line grain; tooltip includes category and revenue.
- Table: products with Revenue, Profit, Units and Returned Lines.

## Page 5 — Data Quality

- Cards: Raw Rows 4,224; Validated Rows 4,180; Rejected Rows 44; Checks Passed 15/15.
- Table from `data/quality/data_quality_checks.csv`.
- Bar chart from rejected-record reason counts.
- Notes: intended grain, acceptance rate, imputed rating count and latest refresh.

## Interaction rules

- Keep page-level slicers synchronized across Pages 1–4.
- Disable cross-highlighting when it makes KPI cards ambiguous.
- Use drill-through for customer and product detail instead of dense default pages.
- Display currency as ₹M on executive visuals and full rupee values in detail tables/tooltips.

