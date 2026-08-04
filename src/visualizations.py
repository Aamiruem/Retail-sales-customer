"""Generate reproducible Matplotlib and Seaborn portfolio charts."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.analysis import dashboard_tables
from src.config import CHARTS_DIR


BLUE = "#2563EB"
GOLD = "#D4A72C"
ORANGE = "#E57A32"
OLIVE = "#7B8B3A"
PINK = "#C65D8A"
INK = "#1F2937"
GRID = "#E5E7EB"


def _style() -> None:
    sns.set_theme(style="whitegrid", font_scale=0.95)
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": GRID,
            "axes.labelcolor": INK,
            "axes.titlecolor": INK,
            "text.color": INK,
            "grid.color": GRID,
            "grid.linewidth": 0.7,
        }
    )


def _save(fig: plt.Figure, filename: str) -> None:
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / filename, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def build_charts(transactions: pd.DataFrame, monthly_targets: pd.DataFrame, rfm: pd.DataFrame) -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    _style()
    tables = dashboard_tables(transactions, monthly_targets, rfm)

    monthly = tables["monthly"].copy()
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.plot(monthly["year_month"], monthly["revenue"] / 1_000_000, color=BLUE, marker="o", linewidth=2.2, label="Revenue")
    ax.plot(monthly["year_month"], monthly["profit"] / 1_000_000, color=GOLD, marker="s", linewidth=2.0, label="Profit")
    ax.set_title("Monthly Revenue and Profit")
    ax.set_ylabel("₹ million")
    ax.tick_params(axis="x", rotation=55)
    ax.legend(frameon=False, ncol=2)
    _save(fig, "01_monthly_revenue_profit.png")

    category = tables["category"].sort_values("revenue")
    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.barh(category["category"], category["revenue"] / 1_000_000, color=BLUE, edgecolor="#1D4ED8")
    for index, value in enumerate(category["revenue"] / 1_000_000):
        ax.text(value + 0.25, index, f"₹{value:.1f}M", va="center", fontsize=9)
    ax.set_title("Revenue by Product Category")
    ax.set_xlabel("₹ million")
    _save(fig, "02_category_performance.png")

    rfm_summary = tables["rfm_summary"].sort_values("customers")
    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.barh(rfm_summary["rfm_segment"], rfm_summary["customers"], color=OLIVE, edgecolor="#58652A")
    ax.set_title("Customers by RFM Segment")
    ax.set_xlabel("Customer count")
    _save(fig, "03_rfm_segments.png")

    sampled = transactions.sample(min(1_200, len(transactions)), random_state=20260804)
    fig, ax = plt.subplots(figsize=(9, 5.4))
    sns.scatterplot(data=sampled, x="discount_pct", y="profit", hue="category", palette=[BLUE, GOLD, ORANGE, OLIVE, PINK], alpha=0.60, s=32, ax=ax)
    ax.axhline(0, color=INK, linewidth=0.9, linestyle="--")
    ax.set_title("Discount and Line Profit Relationship")
    ax.set_xlabel("Discount rate")
    ax.set_ylabel("Profit (₹)")
    ax.xaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    ax.legend(title="Category", frameon=False, bbox_to_anchor=(1.02, 1), loc="upper left")
    _save(fig, "04_discount_profit_relationship.png")

    returns = tables["returns"].sort_values("return_rate")
    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.barh(returns["category"], returns["return_rate"] * 100, color=ORANGE, edgecolor="#B85A1E")
    for index, value in enumerate(returns["return_rate"] * 100):
        ax.text(value + 0.08, index, f"{value:.1f}%", va="center", fontsize=9)
    ax.set_title("Order Return Rate by Category")
    ax.set_xlabel("Returned orders / orders (%)")
    _save(fig, "05_return_rate_by_category.png")

    heat = transactions.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum", fill_value=0) / 1_000_000
    fig, ax = plt.subplots(figsize=(11, 5.8))
    sns.heatmap(heat, annot=True, fmt=".1f", cmap=sns.light_palette(BLUE, as_cmap=True), linewidths=0.7, cbar_kws={"label": "₹ million"}, ax=ax)
    ax.set_title("Revenue by Region and Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Region")
    _save(fig, "06_region_category_heatmap.png")

    fig, ax = plt.subplots(figsize=(11, 5.2))
    x = range(len(monthly))
    ax.bar(x, monthly["target_revenue"] / 1_000_000, color="#DCE6F8", edgecolor="#9DB7E4", label="Target")
    ax.plot(x, monthly["revenue"] / 1_000_000, color=BLUE, marker="o", linewidth=2.2, label="Actual")
    ax.set_xticks(list(x), monthly["year_month"], rotation=55)
    ax.set_ylabel("₹ million")
    ax.set_title("Monthly Revenue versus Target")
    ax.legend(frameon=False, ncol=2)
    _save(fig, "07_target_attainment.png")

    print(f"Created 7 charts in {CHARTS_DIR}")
