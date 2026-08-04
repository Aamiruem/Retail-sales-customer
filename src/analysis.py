"""Reusable analytical transformations for KPIs, RFM and dashboard tables."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_rfm(transactions: pd.DataFrame, snapshot_date: str = "2026-01-01") -> pd.DataFrame:
    snapshot = pd.Timestamp(snapshot_date)
    rfm = (
        transactions.groupby(["customer_id", "customer_name", "customer_segment"], as_index=False)
        .agg(
            last_order_date=("order_date", "max"),
            frequency=("order_id", "nunique"),
            monetary=("revenue", "sum"),
            profit=("profit", "sum"),
            returned_orders=("return_order_flag", "sum"),
        )
    )
    rfm["recency_days"] = (snapshot - pd.to_datetime(rfm["last_order_date"])).dt.days

    rfm["r_score"] = pd.qcut(rfm["recency_days"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["rfm_score"] = rfm["r_score"] * 100 + rfm["f_score"] * 10 + rfm["m_score"]

    conditions = [
        (rfm["r_score"] >= 4) & (rfm["f_score"] >= 4) & (rfm["m_score"] >= 4),
        (rfm["r_score"] >= 3) & (rfm["f_score"] >= 4),
        (rfm["r_score"] >= 4) & (rfm["f_score"].between(2, 3)),
        (rfm["r_score"] == 5) & (rfm["f_score"] == 1),
        (rfm["r_score"] <= 2) & (rfm["f_score"] >= 3),
        (rfm["r_score"] <= 2) & (rfm["f_score"] <= 2),
    ]
    labels = ["Champions", "Loyal Customers", "Potential Loyalists", "New Customers", "At Risk", "Hibernating"]
    rfm["rfm_segment"] = np.select(conditions, labels, default="Needs Attention")
    rfm["monetary"] = rfm["monetary"].round(2)
    rfm["profit"] = rfm["profit"].round(2)
    return rfm.sort_values(["rfm_segment", "monetary"], ascending=[True, False]).reset_index(drop=True)


def kpi_summary(transactions: pd.DataFrame) -> dict[str, float | int]:
    revenue = float(transactions["revenue"].sum())
    profit = float(transactions["profit"].sum())
    orders = int(transactions["order_id"].nunique())
    returned_orders = int(transactions.loc[transactions["return_flag"].eq(1), "order_id"].nunique())
    return {
        "revenue": round(revenue, 2),
        "profit": round(profit, 2),
        "profit_margin": round(profit / revenue if revenue else 0.0, 6),
        "orders": orders,
        "returned_orders": returned_orders,
        "return_rate": round(returned_orders / orders if orders else 0.0, 6),
        "customers": int(transactions["customer_id"].nunique()),
        "average_order_value": round(revenue / orders if orders else 0.0, 2),
        "units_sold": int(transactions.loc[transactions["return_flag"].eq(0), "quantity"].sum()),
    }


def dashboard_tables(transactions: pd.DataFrame, monthly_targets: pd.DataFrame, rfm: pd.DataFrame) -> dict[str, pd.DataFrame]:
    monthly = (
        transactions.groupby("year_month", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            orders=("order_flag", "sum"),
            returned_orders=("return_order_flag", "sum"),
            discount_amount=("discount_amount", "sum"),
        )
        .merge(monthly_targets, on="year_month", how="left")
    )
    monthly["profit_margin"] = monthly["profit"] / monthly["revenue"].replace(0, np.nan)
    monthly["return_rate"] = monthly["returned_orders"] / monthly["orders"].replace(0, np.nan)
    monthly["target_attainment"] = monthly["revenue"] / monthly["target_revenue"].replace(0, np.nan)

    category = (
        transactions.groupby("category", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            order_lines=("line_id", "count"),
            orders=("order_flag", "sum"),
            returned_orders=("return_order_flag", "sum"),
            discount_amount=("discount_amount", "sum"),
        )
    )
    category["profit_margin"] = category["profit"] / category["revenue"].replace(0, np.nan)
    category["return_rate"] = category["returned_orders"] / category["orders"].replace(0, np.nan)
    category = category.sort_values("revenue", ascending=False)

    region = transactions.groupby("region", as_index=False).agg(revenue=("revenue", "sum"), profit=("profit", "sum"), orders=("order_flag", "sum"))
    region["profit_margin"] = region["profit"] / region["revenue"].replace(0, np.nan)
    region = region.sort_values("revenue", ascending=False)

    channel = transactions.groupby("channel", as_index=False).agg(revenue=("revenue", "sum"), profit=("profit", "sum"), orders=("order_flag", "sum"), returned_orders=("return_order_flag", "sum"))
    channel["return_rate"] = channel["returned_orders"] / channel["orders"].replace(0, np.nan)
    channel["profit_margin"] = channel["profit"] / channel["revenue"].replace(0, np.nan)

    rfm_summary = rfm.groupby("rfm_segment", as_index=False).agg(customers=("customer_id", "count"), revenue=("monetary", "sum"), profit=("profit", "sum"))
    rfm_summary = rfm_summary.sort_values("customers", ascending=False)

    discount = transactions.groupby("discount_band", as_index=False, observed=False).agg(revenue=("revenue", "sum"), profit=("profit", "sum"), orders=("order_flag", "sum"))
    discount["profit_margin"] = discount["profit"] / discount["revenue"].replace(0, np.nan)

    returns = category[["category", "orders", "returned_orders", "return_rate"]].copy()
    top_products = transactions.groupby(["product_id", "product_name", "category"], as_index=False).agg(revenue=("revenue", "sum"), profit=("profit", "sum"), quantity=("quantity", "sum"), returned_lines=("return_flag", "sum"))
    top_products = top_products.sort_values("revenue", ascending=False).head(15)

    return {
        "monthly": monthly,
        "category": category,
        "region": region,
        "channel": channel,
        "rfm_summary": rfm_summary,
        "discount": discount,
        "returns": returns,
        "top_products": top_products,
    }

