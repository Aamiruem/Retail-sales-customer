# Project Guide

## Run the Analytics Pipeline

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.run_pipeline
```

This reloads the included CSV, Excel and SQLite raw sources, applies cleaning, writes rejected records, rebuilds the SQLite star schema, exports Power BI tables, recalculates RFM and regenerates the seven static charts.

## Run Tests

```bash
python -m unittest discover -s tests -v
python scripts/verify_project.py
```

## Run Streamlit

```bash
streamlit run streamlit_app/app.py
```

The app loads the final SQLite database and applies user filters in memory. The default view should show ₹160.1M revenue, ₹41.3M profit, 25.8% margin, 3,922 orders and 8.8% return rate.

## Use Excel

Open `excel/Retail_Sales_Customer_Insights_Dashboard.xlsx`. The Dashboard sheet is summary-first; supporting sheets expose formulas and source rows for audit. KPI and summary formulas use bounded ranges through row 4,181.

## Build Power BI

Follow `power_bi/README.md`. After importing the theme and M queries, create relationships, mark the date table, add DAX measures, build pages and run validation queries before saving the compiled PBIX.

## Regenerate Synthetic Sources

```bash
python -m src.generate_data
```

The seed is fixed at `20260804`. The command writes CSV and SQLite sources plus the Excel staging payload. The delivered Excel source is already present and is regenerated in ChatGPT Work using `scripts/build_raw_excel_source.mjs`.

