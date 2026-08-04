"""Data-access and aggregation helpers kept independent from Streamlit UI."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


ENRICHED_QUERY = """
SELECT
    f.line_id,
    f.order_id,
    d.date AS order_date,
    d.year,
    d.quarter,
    d.year_month,
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    c.rfm_segment,
    c.region,
    c.state,
    c.city,
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    s.store_id,
    f.channel,
    f.quantity,
    f.discount_pct,
    f.gross_sales,
    f.discount_amount,
    f.return_flag,
    f.return_amount,
    f.revenue,
    f.cost_amount,
    f.profit,
    f.rating,
    f.order_flag,
    f.return_order_flag,
    f.ship_days,
    t.target_revenue
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_customer c ON f.customer_key = c.customer_key
JOIN dim_product p ON f.product_key = p.product_key
JOIN dim_store s ON f.store_key = s.store_key
JOIN monthly_targets t ON f.year_month = t.year_month
"""


def load_transactions(database_path: str | Path) -> pd.DataFrame:
    with sqlite3.connect(database_path) as connection:
        data = pd.read_sql_query(ENRICHED_QUERY, connection, parse_dates=["order_date"])
    return data


def load_rfm(database_path: str | Path) -> pd.DataFrame:
    with sqlite3.connect(database_path) as connection:
        return pd.read_sql_query("SELECT * FROM customer_rfm", connection, parse_dates=["last_order_date"])


def load_quality_checks(project_root: str | Path) -> pd.DataFrame:
    return pd.read_csv(Path(project_root) / "data" / "quality" / "data_quality_checks.csv")


def apply_filters(
    data: pd.DataFrame,
    date_range: tuple[pd.Timestamp, pd.Timestamp],
    regions: list[str],
    categories: list[str],
    channels: list[str],
    customer_segments: list[str],
) -> pd.DataFrame:
    start_date, end_date = (pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]))
    mask = data["order_date"].between(start_date, end_date)
    if regions:
        mask &= data["region"].isin(regions)
    if categories:
        mask &= data["category"].isin(categories)
    if channels:
        mask &= data["channel"].isin(channels)
    if customer_segments:
        mask &= data["customer_segment"].isin(customer_segments)
    return data.loc[mask].copy()


def calculate_kpis(data: pd.DataFrame) -> dict[str, float | int]:
    revenue = float(data["revenue"].sum())
    profit = float(data["profit"].sum())
    orders = int(data["order_id"].nunique())
    returned_orders = int(data.loc[data["return_flag"].eq(1), "order_id"].nunique())
    return {
        "revenue": revenue,
        "profit": profit,
        "profit_margin": profit / revenue if revenue else 0.0,
        "orders": orders,
        "returned_orders": returned_orders,
        "return_rate": returned_orders / orders if orders else 0.0,
        "average_order_value": revenue / orders if orders else 0.0,
        "customers": int(data["customer_id"].nunique()),
    }


def monthly_performance(data: pd.DataFrame) -> pd.DataFrame:
    grouped = data.groupby("year_month", as_index=False).agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_flag", "sum"),
        returned_orders=("return_order_flag", "sum"),
        target_revenue=("target_revenue", "first"),
    )
    grouped["profit_margin"] = grouped["profit"] / grouped["revenue"].replace(0, np.nan)
    grouped["return_rate"] = grouped["returned_orders"] / grouped["orders"].replace(0, np.nan)
    grouped["target_attainment"] = grouped["revenue"] / grouped["target_revenue"].replace(0, np.nan)
    return grouped.sort_values("year_month")


def category_performance(data: pd.DataFrame) -> pd.DataFrame:
    grouped = data.groupby("category", as_index=False).agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
        returned_orders=("return_order_flag", "sum"),
    )
    grouped["profit_margin"] = grouped["profit"] / grouped["revenue"].replace(0, np.nan)
    grouped["return_rate"] = grouped["returned_orders"] / grouped["orders"].replace(0, np.nan)
    return grouped.sort_values("revenue", ascending=False)


def customer_segment_summary(data: pd.DataFrame) -> pd.DataFrame:
    return (
        data.groupby("rfm_segment", as_index=False)
        .agg(customers=("customer_id", "nunique"), revenue=("revenue", "sum"), profit=("profit", "sum"))
        .sort_values("customers", ascending=False)
    )


def customer_rfm_profile(data: pd.DataFrame) -> pd.DataFrame:
    """Return customer-grain value, activity and recency metrics for the active scope."""
    profile = (
        data.groupby(["customer_id", "customer_name", "customer_segment", "rfm_segment"], as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique"),
            last_order=("order_date", "max"),
        )
    )
    returned = (
        data.loc[data["return_flag"].eq(1)]
        .groupby("customer_id")["order_id"]
        .nunique()
        .rename("returned_orders")
    )
    profile = profile.merge(returned, how="left", left_on="customer_id", right_index=True)
    profile["returned_orders"] = profile["returned_orders"].fillna(0).astype(int)
    reference_date = data["order_date"].max()
    profile["recency_days"] = (reference_date - profile["last_order"]).dt.days.astype(int)
    profile["profit_margin"] = profile["profit"] / profile["revenue"].replace(0, np.nan)
    return profile.sort_values("revenue", ascending=False)


def business_segment_performance(data: pd.DataFrame) -> pd.DataFrame:
    """Summarize customer business segments for the Customer 360 page."""
    result = data.groupby("customer_segment", as_index=False).agg(
        customers=("customer_id", "nunique"),
        orders=("order_id", "nunique"),
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
    )
    result["profit_margin"] = result["profit"] / result["revenue"].replace(0, np.nan)
    return result.sort_values("revenue", ascending=False)


def top_products(data: pd.DataFrame, limit: int = 12) -> pd.DataFrame:
    result = data.groupby(["product_id", "product_name", "category"], as_index=False).agg(
        revenue=("revenue", "sum"), profit=("profit", "sum"), units=("quantity", "sum"), returned_lines=("return_flag", "sum")
    )
    result["profit_margin"] = result["profit"] / result["revenue"].replace(0, np.nan)
    return result.sort_values("revenue", ascending=False).head(limit)
