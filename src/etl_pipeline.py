"""Multi-source extraction, cleaning, enrichment and flat-file delivery."""

from __future__ import annotations

import sqlite3

import numpy as np
import pandas as pd

from src.config import CLEAN_TRANSACTIONS, RAW_CSV, RAW_EXCEL, RAW_SQLITE
from src.data_quality import QualityResult, build_quality_report, clean_and_reject
from src.generate_data import _product_catalog


def load_raw_sources() -> pd.DataFrame:
    csv_data = pd.read_csv(RAW_CSV)
    excel_data = pd.read_excel(RAW_EXCEL, sheet_name="Raw Sales")
    with sqlite3.connect(RAW_SQLITE) as connection:
        sqlite_data = pd.read_sql_query("SELECT * FROM raw_sales", connection)
    raw = pd.concat([csv_data, excel_data, sqlite_data], ignore_index=True, sort=False)
    return raw


def enrich(clean: pd.DataFrame) -> pd.DataFrame:
    clean = clean.sort_values(["order_date", "order_id", "line_id"]).reset_index(drop=True)
    clean["year"] = clean["order_date"].dt.year
    clean["quarter"] = "Q" + clean["order_date"].dt.quarter.astype(str)
    clean["month_no"] = clean["order_date"].dt.month
    clean["month_name"] = clean["order_date"].dt.strftime("%b")
    clean["year_month"] = clean["order_date"].dt.strftime("%Y-%m")
    clean["month_start"] = clean["order_date"].dt.to_period("M").dt.to_timestamp()
    clean["ship_days"] = (clean["ship_date"] - clean["order_date"]).dt.days
    clean["profit_margin"] = np.where(clean["revenue"].ne(0), clean["profit"] / clean["revenue"], np.nan)
    clean["discount_band"] = pd.cut(
        clean["discount_pct"],
        bins=[-0.001, 0.0, 0.10, 0.20, 1.0],
        labels=["No Discount", "1-10%", "11-20%", "Above 20%"],
    )
    clean["order_flag"] = (~clean.duplicated("order_id")).astype(int)
    clean["return_order_flag"] = ((clean["return_flag"].eq(1)) & (~clean.duplicated("order_id"))).astype(int)
    clean["line_number_in_order"] = clean.groupby("order_id").cumcount() + 1
    return clean


def run_etl() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = load_raw_sources()
    product_catalog = _product_catalog()
    result: QualityResult = clean_and_reject(raw, set(product_catalog["product_id"]))
    clean = enrich(result.clean)
    clean.to_csv(CLEAN_TRANSACTIONS, index=False, date_format="%Y-%m-%d")
    checks = build_quality_report(raw, clean, result.rejected, result.rejection_counts, set(product_catalog["product_id"]))
    print(f"ETL complete: {len(raw):,} raw -> {len(clean):,} validated rows; {len(result.rejected):,} rejected.")
    return clean, checks


if __name__ == "__main__":
    run_etl()
