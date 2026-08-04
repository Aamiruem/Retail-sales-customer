# Architecture

## Pipeline Stages

1. **Generate** deterministic synthetic transactions, customer/product reference data and 44 isolated defects.
2. **Extract** 2,112 CSV rows, 1,056 Excel rows and 1,056 SQLite rows.
3. **Validate** grain, keys, required fields, dates, quantities, discount range and product integrity.
4. **Transform** normalized types/strings, imputed optional ratings, calendar attributes, order flags, discount bands and profitability fields.
5. **Model** one fact table, four dimensions, monthly targets and RFM output in SQLite.
6. **Analyze** KPI, trend, category, region, channel, RFM, discount, return and target performance.
7. **Deliver** formula-driven Excel, Power BI source kit, Streamlit application, notebook, charts and reports.
8. **Verify** Python/SQL KPI reconciliation, 15 data-quality rules, referential integrity, workbook render and unit tests.

## Source Precedence

The raw sources are equal partitions of one deterministic synthetic generator. The validated fact table is the analytical source of truth. Dimensions and reports are derived from that fact. `data/database/retail_analytics.db` controls SQL and Streamlit outputs; the processed CSVs control Power BI imports; the clean transaction extract and aggregated payload control the Excel workbook.

## Metric Safety

Multi-line orders would inflate distinct-order metrics if raw row counts were used. `order_flag` and `return_order_flag` equal one only on the first line of each relevant order. Additive dashboard measures can therefore use `SUM` safely across filters.

