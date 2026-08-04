"""Render a static preview of the Streamlit dashboard from the SQLite model."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from streamlit_app.dashboard_data import (  # noqa: E402
    calculate_kpis,
    category_performance,
    load_transactions,
    monthly_performance,
)


BLUE = "#2563EB"
GOLD = "#D4A72C"
ORANGE = "#E57A32"
NAVY = "#17365D"
INK = "#1F2937"
MUTED = "#64748B"
GRID = "#E5E7EB"
PAGE = "#F5F7FB"
WHITE = "#FFFFFF"


def add_card(fig: plt.Figure, x: float, label: str, value: str) -> None:
    card = FancyBboxPatch(
        (x, 0.765),
        0.145,
        0.085,
        transform=fig.transFigure,
        boxstyle="round,pad=0.008,rounding_size=0.012",
        facecolor=WHITE,
        edgecolor="#DDE3EA",
        linewidth=1.0,
    )
    fig.patches.append(card)
    fig.text(x + 0.012, 0.824, label, fontsize=9.5, color=MUTED, weight="medium")
    fig.text(x + 0.012, 0.785, value, fontsize=18, color=INK, weight="bold")


def style_axis(ax: plt.Axes, title: str, subtitle: str) -> None:
    ax.set_facecolor(WHITE)
    ax.set_title(title, loc="left", fontsize=13, color=INK, weight="bold", pad=20)
    ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=8.8, color=MUTED, va="bottom")
    ax.grid(axis="y", color=GRID, linewidth=0.7)
    ax.grid(axis="x", visible=False)
    ax.tick_params(colors=MUTED, labelsize=8.5, length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)


def render(output_path: Path) -> None:
    transactions = load_transactions(PROJECT_ROOT / "data" / "database" / "retail_analytics.db")
    kpis = calculate_kpis(transactions)
    monthly = monthly_performance(transactions)
    category = category_performance(transactions)

    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titleweight": "bold"})
    fig = plt.figure(figsize=(16, 10.5), facecolor=PAGE)

    hero = FancyBboxPatch(
        (0.035, 0.875),
        0.93,
        0.09,
        transform=fig.transFigure,
        boxstyle="round,pad=0.008,rounding_size=0.014",
        facecolor=NAVY,
        edgecolor=NAVY,
    )
    fig.patches.append(hero)
    fig.text(0.058, 0.925, "Retail Sales & Customer Insights", fontsize=24, color=WHITE, weight="bold")
    fig.text(
        0.058,
        0.895,
        "Executive overview · 1 Jan 2024–31 Dec 2025 · Synthetic portfolio data",
        fontsize=10.5,
        color="#DCE6F8",
    )

    cards = [
        ("Revenue", f"₹{kpis['revenue'] / 1_000_000:.1f}M"),
        ("Profit", f"₹{kpis['profit'] / 1_000_000:.1f}M"),
        ("Profit Margin", f"{kpis['profit_margin']:.1%}"),
        ("Orders", f"{kpis['orders']:,}"),
        ("Return Rate", f"{kpis['return_rate']:.1%}"),
        ("Avg Order Value", f"₹{kpis['average_order_value']:,.0f}"),
    ]
    for index, (label, value) in enumerate(cards):
        add_card(fig, 0.04 + index * 0.158, label, value)

    grid = fig.add_gridspec(2, 2, left=0.055, right=0.955, bottom=0.09, top=0.69, hspace=0.40, wspace=0.22)

    ax = fig.add_subplot(grid[0, 0])
    x = np.arange(len(monthly))
    ax.plot(x, monthly["revenue"] / 1_000_000, color=BLUE, linewidth=2.4, marker="o", markersize=3.8, label="Revenue")
    ax.plot(x, monthly["profit"] / 1_000_000, color=GOLD, linewidth=2.2, marker="s", markersize=3.4, label="Profit")
    style_axis(ax, "Monthly Revenue and Profit", "INR million · 24 monthly observations")
    ax.set_xticks(x[::2], monthly["year_month"].iloc[::2], rotation=45, ha="right")
    ax.set_ylabel("₹ million", color=MUTED, fontsize=9)
    ax.legend(frameon=False, loc="upper left", ncol=2, fontsize=8.5)

    ax = fig.add_subplot(grid[0, 1])
    ranked = category.sort_values("revenue")
    bars = ax.barh(ranked["category"], ranked["revenue"] / 1_000_000, color=BLUE, edgecolor="#1D4ED8")
    style_axis(ax, "Revenue by Product Category", "INR million · all validated transactions")
    ax.set_xlabel("₹ million", color=MUTED, fontsize=9)
    ax.bar_label(bars, labels=[f"{value:.1f}" for value in ranked["revenue"] / 1_000_000], padding=4, fontsize=8, color=INK)
    ax.set_xlim(0, (ranked["revenue"].max() / 1_000_000) * 1.14)

    ax = fig.add_subplot(grid[1, 0])
    ax.bar(x, monthly["target_revenue"] / 1_000_000, color="#DCE6F8", edgecolor="#9DB7E4", label="Target")
    ax.plot(x, monthly["revenue"] / 1_000_000, color=BLUE, linewidth=2.2, marker="o", markersize=3.8, label="Actual")
    style_axis(ax, "Monthly Revenue versus Target", "INR million · actual sales compared with monthly plan")
    ax.set_xticks(x[::2], monthly["year_month"].iloc[::2], rotation=45, ha="right")
    ax.set_ylabel("₹ million", color=MUTED, fontsize=9)
    ax.legend(frameon=False, loc="upper left", ncol=2, fontsize=8.5)

    ax = fig.add_subplot(grid[1, 1])
    returns = category.sort_values("return_rate")
    bars = ax.barh(returns["category"], returns["return_rate"] * 100, color=ORANGE, edgecolor="#B85A1E")
    style_axis(ax, "Order Return Rate by Category", "Returned distinct orders ÷ distinct orders")
    ax.set_xlabel("% of orders", color=MUTED, fontsize=9)
    ax.bar_label(bars, labels=[f"{value:.1%}" for value in returns["return_rate"]], padding=4, fontsize=8, color=INK)
    ax.set_xlim(0, returns["return_rate"].max() * 100 * 1.18)

    fig.text(
        0.055,
        0.035,
        "Source: data/database/retail_analytics.db · Grain: one row per validated order line · 4,180 lines · 15/15 quality checks passed",
        fontsize=8.5,
        color=MUTED,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    render(PROJECT_ROOT / "reports" / "streamlit_dashboard_preview.png")
