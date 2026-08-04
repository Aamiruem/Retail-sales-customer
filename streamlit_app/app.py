from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from streamlit_app.dashboard_data import (
    apply_filters,
    calculate_kpis,
    category_performance,
    customer_segment_summary,
    load_quality_checks,
    load_transactions,
    monthly_performance,
    top_products,
)


st.set_page_config(
    page_title="Retail Sales & Customer Insights",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATABASE_PATH = PROJECT_ROOT / "data" / "database" / "retail_analytics.db"

BLUE = "#2563EB"
GOLD = "#D4A72C"
ORANGE = "#E57A32"
OLIVE = "#7B8B3A"
PINK = "#C65D8A"
NAVY = "#17365D"
INK = "#1F2937"
GRID = "#E5E7EB"
PALETTE = [BLUE, GOLD, ORANGE, OLIVE, PINK]

st.markdown(
    """
    <style>
      .stApp { background: #F5F7FB; }
      [data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #DDE3EA; }
      .hero { background:#17365D; color:#FFFFFF; padding:1.2rem 1.4rem; border-radius:12px; margin-bottom:1rem; }
      .hero h1 { margin:0; font-size:2rem; }
      .hero p { margin:.35rem 0 0; color:#DCE6F8; }
      div[data-testid="stMetric"] { background:#FFFFFF; border:1px solid #DDE3EA; border-radius:10px; padding:.8rem 1rem; }
      div[data-testid="stMetricLabel"] { color:#64748B; }
      .section-note { color:#64748B; font-size:.88rem; margin-top:-.4rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def cached_transactions(path: str) -> pd.DataFrame:
    return load_transactions(path)


@st.cache_data(show_spinner=False)
def cached_quality(project_root: str) -> pd.DataFrame:
    return load_quality_checks(project_root)


def format_inr_millions(value: float) -> str:
    return f"₹{value / 1_000_000:,.1f}M"


def chart_style(ax: plt.Axes, title: str, ylabel: str = "") -> None:
    ax.set_title(title, loc="left", fontsize=13, color=INK, pad=12, fontweight="semibold")
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", color=GRID, linewidth=0.7)
    ax.grid(axis="x", visible=False)
    for spine in ax.spines.values():
        spine.set_visible(False)


try:
    transactions = cached_transactions(str(DATABASE_PATH))
except Exception as exc:
    st.error(f"The analytics database could not be loaded: {exc}")
    st.stop()

st.markdown(
    """
    <div class="hero">
      <h1>Retail Sales & Customer Insights</h1>
      <p>Executive KPIs, customer RFM, category performance, discounts, returns and targets · Synthetic portfolio data</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Dashboard Filters")
    min_date = transactions["order_date"].min().date()
    max_date = transactions["order_date"].max().date()
    selected_dates = st.date_input("Order date", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    if not isinstance(selected_dates, tuple) or len(selected_dates) != 2:
        selected_dates = (min_date, max_date)

    selected_regions = st.multiselect("Region", sorted(transactions["region"].unique()), default=[])
    selected_categories = st.multiselect("Category", sorted(transactions["category"].unique()), default=[])
    selected_channels = st.multiselect("Channel", sorted(transactions["channel"].unique()), default=[])
    selected_segments = st.multiselect("Customer segment", sorted(transactions["customer_segment"].unique()), default=[])
    st.caption("Empty selections mean all values.")
    st.divider()
    st.caption("Data: 1 Jan 2024–31 Dec 2025 · 4,180 validated lines · INR")

filtered = apply_filters(
    transactions,
    (pd.Timestamp(selected_dates[0]), pd.Timestamp(selected_dates[1])),
    selected_regions,
    selected_categories,
    selected_channels,
    selected_segments,
)

if filtered.empty:
    st.warning("No transactions match the selected filters. Remove one or more filters to continue.")
    st.stop()

kpis = calculate_kpis(filtered)
metric_columns = st.columns(6)
metric_columns[0].metric("Revenue", format_inr_millions(kpis["revenue"]))
metric_columns[1].metric("Profit", format_inr_millions(kpis["profit"]))
metric_columns[2].metric("Profit Margin", f"{kpis['profit_margin']:.1%}")
metric_columns[3].metric("Orders", f"{kpis['orders']:,}")
metric_columns[4].metric("Return Rate", f"{kpis['return_rate']:.1%}")
metric_columns[5].metric("Avg Order Value", f"₹{kpis['average_order_value']:,.0f}")

overview_tab, customer_tab, product_tab, quality_tab = st.tabs(["Executive Overview", "Customer RFM", "Products & Returns", "Data Quality"])

with overview_tab:
    monthly = monthly_performance(filtered)
    left, right = st.columns([1.25, 1])
    with left:
        fig, ax = plt.subplots(figsize=(9.2, 4.3))
        ax.plot(monthly["year_month"], monthly["revenue"] / 1_000_000, color=BLUE, linewidth=2.3, marker="o", label="Revenue")
        ax.plot(monthly["year_month"], monthly["profit"] / 1_000_000, color=GOLD, linewidth=2.1, marker="s", label="Profit")
        chart_style(ax, "Monthly Revenue and Profit", "₹ million")
        ax.tick_params(axis="x", rotation=55, labelsize=8)
        ax.legend(frameon=False, ncol=2)
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    with right:
        category = category_performance(filtered).sort_values("revenue")
        fig, ax = plt.subplots(figsize=(7.2, 4.3))
        ax.barh(category["category"], category["revenue"] / 1_000_000, color=BLUE, edgecolor="#1D4ED8")
        chart_style(ax, "Revenue by Product Category", "₹ million")
        st.pyplot(fig, width="stretch")
        plt.close(fig)

    left, right = st.columns([1.25, 1])
    with left:
        fig, ax = plt.subplots(figsize=(9.2, 4.2))
        x = np.arange(len(monthly))
        ax.bar(x, monthly["target_revenue"] / 1_000_000, color="#DCE6F8", edgecolor="#9DB7E4", label="Target")
        ax.plot(x, monthly["revenue"] / 1_000_000, color=BLUE, marker="o", linewidth=2.2, label="Actual")
        ax.set_xticks(x, monthly["year_month"], rotation=55, fontsize=8)
        chart_style(ax, "Monthly Revenue versus Target", "₹ million")
        ax.legend(frameon=False, ncol=2)
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    with right:
        heat = filtered.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum", fill_value=0) / 1_000_000
        fig, ax = plt.subplots(figsize=(7.2, 4.2))
        sns.heatmap(heat, annot=True, fmt=".1f", cmap=sns.light_palette(BLUE, as_cmap=True), linewidths=0.6, cbar_kws={"label": "₹M"}, ax=ax)
        ax.set_title("Revenue by Region and Category", loc="left", fontsize=13, color=INK, fontweight="semibold")
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(axis="x", rotation=35, labelsize=8)
        st.pyplot(fig, width="stretch")
        plt.close(fig)

with customer_tab:
    segment = customer_segment_summary(filtered)
    left, right = st.columns([1, 1.2])
    with left:
        ordered = segment.sort_values("customers")
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        ax.barh(ordered["rfm_segment"], ordered["customers"], color=OLIVE, edgecolor="#58652A")
        chart_style(ax, "Customers by RFM Segment", "Customers")
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    with right:
        customer_summary = (
            filtered.groupby(["customer_id", "customer_name", "rfm_segment"], as_index=False)
            .agg(revenue=("revenue", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"), last_order=("order_date", "max"))
            .sort_values("revenue", ascending=False)
            .head(15)
        )
        customer_summary["revenue"] = customer_summary["revenue"].map(lambda value: f"₹{value:,.0f}")
        customer_summary["profit"] = customer_summary["profit"].map(lambda value: f"₹{value:,.0f}")
        customer_summary["last_order"] = customer_summary["last_order"].dt.strftime("%Y-%m-%d")
        st.subheader("Top Customers by Revenue")
        st.caption("Exact-value lookup after the segment overview.")
        st.table(customer_summary.rename(columns=str.title))

with product_tab:
    category = category_performance(filtered)
    left, right = st.columns(2)
    with left:
        returns = category.sort_values("return_rate")
        fig, ax = plt.subplots(figsize=(7.4, 4.5))
        ax.barh(returns["category"], returns["return_rate"] * 100, color=ORANGE, edgecolor="#B85A1E")
        chart_style(ax, "Order Return Rate by Category", "% of orders")
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    with right:
        sample = filtered.sample(min(1_200, len(filtered)), random_state=20260804)
        fig, ax = plt.subplots(figsize=(7.4, 4.5))
        sns.scatterplot(data=sample, x="discount_pct", y="profit", hue="category", palette=PALETTE, alpha=0.62, s=30, ax=ax)
        ax.axhline(0, color=INK, linestyle="--", linewidth=0.9)
        chart_style(ax, "Discount and Line Profit Relationship", "Profit (₹)")
        ax.xaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
        ax.legend(frameon=False, fontsize=7, title="Category")
        st.pyplot(fig, width="stretch")
        plt.close(fig)

    products = top_products(filtered)
    products["revenue"] = products["revenue"].map(lambda value: f"₹{value:,.0f}")
    products["profit"] = products["profit"].map(lambda value: f"₹{value:,.0f}")
    products["profit_margin"] = products["profit_margin"].map(lambda value: f"{value:.1%}")
    st.subheader("Top Products")
    st.table(products.rename(columns=str.title))

with quality_tab:
    checks = cached_quality(str(PROJECT_ROOT))
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Raw Rows", "4,224")
    q2.metric("Validated Rows", "4,180")
    q3.metric("Rejected Rows", "44")
    q4.metric("Checks Passed", f"{int(checks['passed'].sum())}/{len(checks)}")
    st.subheader("Automated Quality Checks")
    displayed_checks = checks[["check_id", "check_name", "actual", "expected", "severity", "status"]].copy()
    st.table(displayed_checks.rename(columns=str.title))
    st.info("Dataset grain: one row per order line. All figures are synthetic and intended for portfolio demonstration.")

st.download_button(
    "Download filtered transactions (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_retail_transactions.csv",
    mime="text/csv",
)
