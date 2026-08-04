"""Validate the full project contract before packaging or publishing."""

from __future__ import annotations

import json
import sqlite3
import sys
import zipfile
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "data/raw/retail_sales_source_a.csv",
    "data/raw/retail_sales_source_b.xlsx",
    "data/raw/retail_sales_source_c.db",
    "data/processed/retail_transactions_clean.csv",
    "data/processed/fact_sales.csv",
    "data/processed/dim_date.csv",
    "data/processed/dim_customer.csv",
    "data/processed/dim_product.csv",
    "data/database/retail_analytics.db",
    "excel/Retail_Sales_Customer_Insights_Dashboard.xlsx",
    "power_bi/power_query/Load_Star_Schema.m",
    "power_bi/dax/Measures.dax",
    "power_bi/theme/Retail_Insights_Theme.json",
    "streamlit_app/app.py",
    "notebooks/retail_sales_customer_insights_analysis.ipynb",
    "reports/executive_summary.md",
    "reports/data_quality_report.md",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def verify() -> None:
    missing = [path for path in REQUIRED_FILES if not (PROJECT_ROOT / path).exists()]
    if missing:
        fail(f"Missing required files: {missing}")

    quality = json.loads((PROJECT_ROOT / "data/quality/data_quality_summary.json").read_text(encoding="utf-8"))
    if quality["overall_status"] != "READY" or quality["checks_passed"] != quality["checks_total"]:
        fail("Data quality contract is not READY")

    with sqlite3.connect(PROJECT_ROOT / "data/database/retail_analytics.db") as connection:
        result = connection.execute(
            "SELECT COUNT(*), COUNT(DISTINCT line_id), ROUND(SUM(revenue),2), ROUND(SUM(profit),2), SUM(order_flag), SUM(return_order_flag) FROM fact_sales"
        ).fetchone()
        expected = (4_180, 4_180, 160_100_000.0, 41_300_000.0, 3_922, 345)
        if result != expected:
            fail(f"KPI reconciliation failed: {result} != {expected}")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            fail("Foreign-key violations found")

    checks = pd.read_csv(PROJECT_ROOT / "data/quality/data_quality_checks.csv")
    if len(checks) != 15 or not checks["passed"].all():
        fail("Automated data-quality checks failed")

    json.loads((PROJECT_ROOT / "power_bi/theme/Retail_Insights_Theme.json").read_text(encoding="utf-8"))
    notebook = json.loads((PROJECT_ROOT / "notebooks/retail_sales_customer_insights_analysis.ipynb").read_text(encoding="utf-8"))
    if notebook.get("nbformat") != 4 or not notebook.get("cells"):
        fail("Notebook structure is invalid")
    if any(cell.get("cell_type") == "code" and cell.get("execution_count") is None for cell in notebook["cells"]):
        fail("Notebook contains unexecuted code cells")

    for xlsx_path in [
        PROJECT_ROOT / "data/raw/retail_sales_source_b.xlsx",
        PROJECT_ROOT / "excel/Retail_Sales_Customer_Insights_Dashboard.xlsx",
    ]:
        if not zipfile.is_zipfile(xlsx_path):
            fail(f"Invalid XLSX package: {xlsx_path}")

    print("PASS: all required files, KPIs, quality checks, relationships, JSON files, notebook cells and XLSX packages are valid.")


if __name__ == "__main__":
    verify()

