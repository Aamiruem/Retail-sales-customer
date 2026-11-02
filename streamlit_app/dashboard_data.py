"""Data-access and aggregation helpers kept independent from Streamlit UI."""

from __future__ import annotations

import json
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


def load_quality_summary(project_root: str | Path) -> dict:
    """Pipeline quality summary (row counts, checks passed) written by the ETL run."""
    path = Path(project_root) / "data" / "quality" / "data_quality_summary.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def has_scope_filters(regions, categories, channels, customer_segments) -> bool:
    """True when the view is narrowed below company level (targets are company-wide)."""
    return any([regions, categories, channels, customer_segments])


def discount_band_performance(data: pd.DataFrame) -> pd.DataFrame:
    """Revenue, profit and margin per discount band (readable alternative to a scatter)."""
    bands = pd.cut(
        data["discount_pct"],
        bins=[-0.001, 0.05, 0.10, 0.15, 0.20, 1.0],
        labels=["0–5%", "5–10%", "10–15%", "15–20%", "20%+"],
    )
    result = (
        data.assign(discount_band=bands)
        .groupby("discount_band", observed=True, as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            lines=("line_id", "size"),
            loss_lines=("profit", lambda values: int((values < 0).sum())),
        )
    )
    result["profit_margin"] = result["profit"] / result["revenue"].replace(0, np.nan)
    result["loss_share"] = result["loss_lines"] / result["lines"].replace(0, np.nan)
    return result


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


def _returned_orders_by(data: pd.DataFrame, key: str) -> pd.DataFrame:
    return (
        data.loc[data["return_flag"].eq(1)]
        .groupby(key)["order_id"]
        .nunique()
        .rename("returned_orders")
        .reset_index()
    )


def monthly_performance(data: pd.DataFrame) -> pd.DataFrame:
    # Distinct-order counts stay correct when filters split an order's lines.
    grouped = data.groupby("year_month", as_index=False).agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
        target_revenue=("target_revenue", "first"),
    )
    grouped = grouped.merge(_returned_orders_by(data, "year_month"), on="year_month", how="left")
    grouped["returned_orders"] = grouped["returned_orders"].fillna(0).astype(int)
    grouped["profit_margin"] = grouped["profit"] / grouped["revenue"].replace(0, np.nan)
    grouped["return_rate"] = grouped["returned_orders"] / grouped["orders"].replace(0, np.nan)
    grouped["target_attainment"] = grouped["revenue"] / grouped["target_revenue"].replace(0, np.nan)
    return grouped.sort_values("year_month")


def category_performance(data: pd.DataFrame) -> pd.DataFrame:
    grouped = data.groupby("category", as_index=False).agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
    )
    grouped = grouped.merge(_returned_orders_by(data, "category"), on="category", how="left")
    grouped["returned_orders"] = grouped["returned_orders"].fillna(0).astype(int)
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


def customer_ml_clusters(data: pd.DataFrame, requested_clusters: int = 4) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create deterministic K-Means customer groups from recency, frequency and value."""
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    profile = customer_rfm_profile(data).copy()
    cluster_count = min(requested_clusters, len(profile))
    if cluster_count == 1:
        profile["ml_cluster_id"] = 0
        profile["ml_cluster"] = "Single Active Group"
    else:
        features = np.column_stack(
            [
                profile["recency_days"].to_numpy(dtype=float),
                np.log1p(profile["orders"].to_numpy(dtype=float)),
                np.log1p(profile["revenue"].to_numpy(dtype=float)),
            ]
        )
        scaled = StandardScaler().fit_transform(features)
        model = KMeans(n_clusters=cluster_count, random_state=20260804, n_init=20)
        profile["ml_cluster_id"] = model.fit_predict(scaled)

        centers = profile.groupby("ml_cluster_id", as_index=False).agg(
            recency_days=("recency_days", "mean"),
            orders=("orders", "mean"),
            revenue=("revenue", "mean"),
        )
        value_score = (
            -centers["recency_days"].rank(pct=True)
            + centers["orders"].rank(pct=True)
            + centers["revenue"].rank(pct=True)
        )
        centers = centers.assign(value_score=value_score).sort_values("value_score", ascending=False)
        cluster_names = ["High Value", "Loyal Growth", "Developing", "Needs Attention"]
        name_map = {
            int(cluster_id): cluster_names[min(index, len(cluster_names) - 1)]
            for index, cluster_id in enumerate(centers["ml_cluster_id"])
        }
        profile["ml_cluster"] = profile["ml_cluster_id"].map(name_map)

    summary = profile.groupby(["ml_cluster_id", "ml_cluster"], as_index=False).agg(
        customers=("customer_id", "nunique"),
        average_recency_days=("recency_days", "mean"),
        average_orders=("orders", "mean"),
        average_revenue=("revenue", "mean"),
        total_revenue=("revenue", "sum"),
        total_profit=("profit", "sum"),
    )
    summary["profit_margin"] = summary["total_profit"] / summary["total_revenue"].replace(0, np.nan)
    return profile, summary.sort_values("average_revenue", ascending=False)


def statistical_snapshot(data: pd.DataFrame) -> dict[str, float | int]:
    """Return a compact descriptive-statistics snapshot for the active scope."""
    revenue = data["revenue"].astype(float)
    profit = data["profit"].astype(float)
    discount = data["discount_pct"].astype(float)
    order_returns = data.groupby("order_id")["return_flag"].max()
    order_count = int(len(order_returns))
    return_rate = float(order_returns.mean()) if order_count else 0.0
    standard_error = np.sqrt(return_rate * (1 - return_rate) / order_count) if order_count else 0.0
    return {
        "line_revenue_mean": float(revenue.mean()),
        "line_revenue_median": float(revenue.median()),
        "line_revenue_std": float(revenue.std(ddof=1)),
        "profit_median": float(profit.median()),
        "average_discount": float(discount.mean()),
        "discount_profit_correlation": float(discount.corr(profit)),
        "return_rate": return_rate,
        "return_rate_ci_low": max(0.0, return_rate - 1.96 * standard_error),
        "return_rate_ci_high": min(1.0, return_rate + 1.96 * standard_error),
        "orders": order_count,
    }


def top_products(data: pd.DataFrame, limit: int = 12) -> pd.DataFrame:
    result = data.groupby(["product_id", "product_name", "category"], as_index=False).agg(
        revenue=("revenue", "sum"), profit=("profit", "sum"), units=("quantity", "sum"), returned_lines=("return_flag", "sum")
    )
    result["profit_margin"] = result["profit"] / result["revenue"].replace(0, np.nan)
    return result.sort_values("revenue", ascending=False).head(limit)
