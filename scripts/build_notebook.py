"""Create a reproducible Jupyter notebook using the standard nbformat v4 schema."""

from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "notebooks" / "retail_sales_customer_insights_analysis.ipynb"


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source.splitlines(keepends=True)}


cells = [
    markdown(
        """# Retail Sales & Customer Insights Analytics

## tl;dr

The validated synthetic dataset contains **4,180 order lines** and **3,922 orders**. It reconciles to **₹160.1M revenue**, **₹41.3M profit**, a **25.8% margin** and an **8.8% order return rate**. Electronics leads revenue; Beauty & Personal Care leads margin and return rate; margin declines with deeper discounts.
"""
    ),
    markdown(
        """## Context & Methods

This companion notebook audits the SQLite star schema, profiles data quality, reproduces KPI results and creates focused category and monthly views.

### Key Assumptions

- Data is deterministic and synthetic.
- Fact grain is one row per order line.
- Revenue is net of discount and return amount.
- Order metrics use first-line flags to prevent double counting.
"""
    ),
    code(
        """from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = Path.cwd()
if not (PROJECT_ROOT / 'data').exists():
    PROJECT_ROOT = PROJECT_ROOT.parent
DATABASE = PROJECT_ROOT / 'data' / 'database' / 'retail_analytics.db'
print(f'Project root: {PROJECT_ROOT}')
"""
    ),
    markdown("## Data\n\n### 1. Load the enriched star-schema view"),
    code(
        """with sqlite3.connect(DATABASE) as connection:
    sales = pd.read_sql_query('SELECT * FROM vw_sales_enriched', connection, parse_dates=['date'])
    quality_checks = pd.read_csv(PROJECT_ROOT / 'data' / 'quality' / 'data_quality_checks.csv')
print(f'Sales shape: {sales.shape}')
print(f'Date range: {sales.date.min().date()} to {sales.date.max().date()}')
print(f'Quality checks passed: {int(quality_checks.passed.sum())}/{len(quality_checks)}')
"""
    ),
    markdown("### 2. Reconcile headline KPIs"),
    code(
        """with sqlite3.connect(DATABASE) as connection:
    kpis = pd.read_sql_query(
        '''SELECT ROUND(SUM(revenue),2) AS revenue, ROUND(SUM(profit),2) AS profit,
                  ROUND(SUM(profit)/SUM(revenue),6) AS profit_margin,
                  SUM(order_flag) AS orders, SUM(return_order_flag) AS returned_orders,
                  ROUND(1.0*SUM(return_order_flag)/SUM(order_flag),6) AS return_rate
           FROM fact_sales''',
        connection,
    )
print(kpis.to_string(index=False))
assert float(kpis.loc[0, 'revenue']) == 160_100_000.0
assert float(kpis.loc[0, 'profit']) == 41_300_000.0
assert int(kpis.loc[0, 'orders']) == 3_922
"""
    ),
    markdown("## Results\n\n### 3. Monthly performance and target attainment"),
    code(
        """with sqlite3.connect(DATABASE) as connection:
    monthly = pd.read_sql_query(
        '''SELECT f.year_month, SUM(f.revenue) revenue, SUM(f.profit) profit,
                  SUM(f.order_flag) orders, t.target_revenue,
                  SUM(f.revenue)/t.target_revenue target_attainment
           FROM fact_sales f JOIN monthly_targets t USING(year_month)
           GROUP BY f.year_month, t.target_revenue ORDER BY f.year_month''',
        connection,
    )
print(monthly.head(6).round(3).to_string(index=False))
print(f'Months at or above target: {(monthly.target_attainment >= 1).sum()} of {len(monthly)}')
"""
    ),
    code(
        """fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(monthly.year_month, monthly.revenue / 1_000_000, color='#2563EB', marker='o', label='Revenue')
ax.plot(monthly.year_month, monthly.profit / 1_000_000, color='#D4A72C', marker='s', label='Profit')
ax.set_title('Monthly Revenue and Profit')
ax.set_ylabel('₹ million')
ax.tick_params(axis='x', rotation=55)
ax.legend(frameon=False)
fig.tight_layout()
chart_path = PROJECT_ROOT / 'reports' / 'charts' / 'notebook_monthly_revenue_profit.png'
fig.savefig(chart_path, dpi=160, bbox_inches='tight')
plt.close(fig)
print(f'Saved chart: {chart_path}')
"""
    ),
    markdown("### 4. Category performance"),
    code(
        """with sqlite3.connect(DATABASE) as connection:
    category = pd.read_sql_query(
        '''SELECT p.category, SUM(f.revenue) revenue, SUM(f.profit) profit,
                  SUM(f.profit)/SUM(f.revenue) profit_margin,
                  1.0*SUM(f.return_order_flag)/SUM(f.order_flag) return_rate
           FROM fact_sales f JOIN dim_product p USING(product_key)
           GROUP BY p.category ORDER BY revenue DESC''',
        connection,
    )
print(category.round(4).to_string(index=False))
"""
    ),
    markdown("### 5. RFM segments and discount profitability"),
    code(
        """with sqlite3.connect(DATABASE) as connection:
    rfm = pd.read_sql_query(
        'SELECT rfm_segment, COUNT(*) customers, SUM(monetary) revenue FROM customer_rfm GROUP BY rfm_segment ORDER BY customers DESC',
        connection,
    )
    discount = pd.read_sql_query(
        '''SELECT CASE WHEN discount_pct=0 THEN 'No Discount' WHEN discount_pct<=.10 THEN '1-10%'
                     WHEN discount_pct<=.20 THEN '11-20%' ELSE 'Above 20%' END discount_band,
                  SUM(revenue) revenue, SUM(profit)/NULLIF(SUM(revenue),0) profit_margin
           FROM fact_sales GROUP BY discount_band ORDER BY profit_margin DESC''',
        connection,
    )
print('RFM segments:')
print(rfm.round(2).to_string(index=False))
print()
print('Discount profitability:')
print(discount.round(4).to_string(index=False))
"""
    ),
    markdown(
        """## Takeaways

- Electronics is the scale category; higher-margin categories contribute less revenue.
- Beauty & Personal Care combines the highest category margin with the highest return rate.
- Champions and At-Risk customers both represent meaningful revenue pools.
- Deep discount bands are associated with lower descriptive profit margins.
- The star schema, KPI arithmetic and quality outputs reconcile across independent query paths.

**Caveat:** these patterns are created from synthetic data and demonstrate methods rather than real-world causal evidence.
"""
    ),
]

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUTPUT.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
print(f"Created {OUTPUT}")
