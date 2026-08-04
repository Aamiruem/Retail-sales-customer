"""Create Power BI-ready dimensions, facts and the SQLite star schema."""

from __future__ import annotations

import sqlite3

import numpy as np
import pandas as pd

from src.analysis import compute_rfm
from src.config import (
    ANALYTICS_DB,
    DIM_CUSTOMER_CSV,
    DIM_DATE_CSV,
    DIM_PRODUCT_CSV,
    DIM_STORE_CSV,
    FACT_SALES_CSV,
    MONTHLY_TARGETS_CSV,
    PROJECT_ROOT,
    RFM_SEGMENTS_CSV,
)


def _build_date_dimension(clean: pd.DataFrame) -> pd.DataFrame:
    dates = pd.date_range(clean["order_date"].min().normalize(), clean["order_date"].max().normalize(), freq="D")
    dim = pd.DataFrame({"date": dates})
    dim["date_key"] = dim["date"].dt.strftime("%Y%m%d").astype(int)
    dim["year"] = dim["date"].dt.year
    dim["quarter"] = "Q" + dim["date"].dt.quarter.astype(str)
    dim["month_no"] = dim["date"].dt.month
    dim["month_name"] = dim["date"].dt.strftime("%B")
    dim["year_month"] = dim["date"].dt.strftime("%Y-%m")
    dim["week_of_year"] = dim["date"].dt.isocalendar().week.astype(int)
    dim["day_name"] = dim["date"].dt.day_name()
    dim["is_weekend"] = dim["date"].dt.dayofweek.ge(5).astype(int)
    return dim[["date_key", "date", "year", "quarter", "month_no", "month_name", "year_month", "week_of_year", "day_name", "is_weekend"]]


def _build_targets(clean: pd.DataFrame) -> pd.DataFrame:
    monthly = clean.groupby("year_month", as_index=False).agg(actual_revenue=("revenue", "sum"), actual_profit=("profit", "sum"))
    factors = np.array([0.96, 0.98, 1.00, 1.02, 1.04, 1.06, 1.03, 1.01, 0.99, 1.05, 1.07, 1.08] * 2)[: len(monthly)]
    monthly["target_revenue"] = (monthly["actual_revenue"] * factors).round(2)
    monthly["target_profit"] = (monthly["target_revenue"] * 0.258).round(2)
    return monthly[["year_month", "target_revenue", "target_profit"]]


def build_star_schema(clean: pd.DataFrame) -> dict[str, pd.DataFrame]:
    rfm = compute_rfm(clean)
    dim_date = _build_date_dimension(clean)

    customer_attributes = (
        clean.sort_values("order_date")
        .drop_duplicates("customer_id")[["customer_id", "customer_name", "customer_segment", "region", "state", "city"]]
    )
    dim_customer = customer_attributes.merge(rfm[["customer_id", "recency_days", "frequency", "monetary", "r_score", "f_score", "m_score", "rfm_score", "rfm_segment"]], on="customer_id", how="left")
    dim_customer = dim_customer.sort_values("customer_id").reset_index(drop=True)
    dim_customer.insert(0, "customer_key", np.arange(1, len(dim_customer) + 1))

    dim_product = clean.drop_duplicates("product_id")[["product_id", "product_name", "category", "subcategory"]].sort_values("product_id").reset_index(drop=True)
    dim_product.insert(0, "product_key", np.arange(1, len(dim_product) + 1))

    dim_store = clean.drop_duplicates("store_id")[["store_id", "channel"]].sort_values("store_id").reset_index(drop=True)
    dim_store.insert(0, "store_key", np.arange(1, len(dim_store) + 1))

    targets = _build_targets(clean)

    fact = clean.copy()
    fact["date_key"] = fact["order_date"].dt.strftime("%Y%m%d").astype(int)
    fact = fact.merge(dim_customer[["customer_key", "customer_id"]], on="customer_id", how="left", validate="many_to_one")
    fact = fact.merge(dim_product[["product_key", "product_id"]], on="product_id", how="left", validate="many_to_one")
    fact = fact.merge(dim_store[["store_key", "store_id"]], on="store_id", how="left", validate="many_to_one")
    fact.insert(0, "sale_key", np.arange(1, len(fact) + 1))
    fact_columns = [
        "sale_key",
        "line_id",
        "order_id",
        "date_key",
        "customer_key",
        "product_key",
        "store_key",
        "channel",
        "quantity",
        "unit_price",
        "discount_pct",
        "gross_sales",
        "discount_amount",
        "sales_after_discount",
        "return_flag",
        "return_amount",
        "revenue",
        "unit_cost",
        "cost_amount",
        "profit",
        "payment_method",
        "rating",
        "rating_was_imputed",
        "order_flag",
        "return_order_flag",
        "ship_days",
        "year_month",
    ]
    fact = fact[fact_columns]

    dim_date.to_csv(DIM_DATE_CSV, index=False, date_format="%Y-%m-%d")
    dim_customer.to_csv(DIM_CUSTOMER_CSV, index=False)
    dim_product.to_csv(DIM_PRODUCT_CSV, index=False)
    dim_store.to_csv(DIM_STORE_CSV, index=False)
    fact.to_csv(FACT_SALES_CSV, index=False)
    targets.to_csv(MONTHLY_TARGETS_CSV, index=False)
    rfm.to_csv(RFM_SEGMENTS_CSV, index=False, date_format="%Y-%m-%d")

    if ANALYTICS_DB.exists():
        ANALYTICS_DB.unlink()
    schema_sql = (PROJECT_ROOT / "sql" / "01_create_star_schema.sql").read_text(encoding="utf-8")
    with sqlite3.connect(ANALYTICS_DB) as connection:
        connection.executescript(schema_sql)
        dim_date.assign(date=dim_date["date"].dt.strftime("%Y-%m-%d")).to_sql("dim_date", connection, if_exists="append", index=False)
        dim_customer.to_sql("dim_customer", connection, if_exists="append", index=False)
        dim_product.to_sql("dim_product", connection, if_exists="append", index=False)
        dim_store.to_sql("dim_store", connection, if_exists="append", index=False)
        targets.to_sql("monthly_targets", connection, if_exists="append", index=False)
        fact.to_sql("fact_sales", connection, if_exists="append", index=False)
        rfm.assign(last_order_date=pd.to_datetime(rfm["last_order_date"]).dt.strftime("%Y-%m-%d")).to_sql("customer_rfm", connection, if_exists="append", index=False)
        connection.execute("ANALYZE")

    print(f"Star schema built: {len(fact):,} fact rows, {len(dim_customer):,} customers, {len(dim_product):,} products.")
    return {
        "fact_sales": fact,
        "dim_date": dim_date,
        "dim_customer": dim_customer,
        "dim_product": dim_product,
        "dim_store": dim_store,
        "monthly_targets": targets,
        "customer_rfm": rfm,
    }


if __name__ == "__main__":
    from src.config import CLEAN_TRANSACTIONS

    data = pd.read_csv(CLEAN_TRANSACTIONS, parse_dates=["order_date", "ship_date", "month_start"])
    build_star_schema(data)
