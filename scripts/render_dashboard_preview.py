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
    top_products,
)


BLUE = "#2563EB"
PURPLE = "#7C3AED"
CYAN = "#0891B2"
GOLD = "#D4A72C"
ORANGE = "#E57A32"
OLIVE = "#7B8B3A"
PINK = "#C65D8A"
NAVY = "#17365D"
INK = "#1F2937"
MUTED = "#64748B"
GRID = "#E5E7EB"
PAGE = "#EEF4FF"
WHITE = "#FFFFFF"


PALETTE = [BLUE, PURPLE, CYAN, GOLD, ORANGE, OLIVE, PINK]


def add_card(fig: plt.Figure, x: float, label: str, value: str, color: str) -> None:
    card = FancyBboxPatch(
        (x, 0.765),
        0.100,
        0.085,
        transform=fig.transFigure,
        boxstyle="round,pad=0.008,rounding_size=0.012",
        facecolor=WHITE,
        edgecolor="#DDE3EA",
        linewidth=1.0,
    )
    fig.patches.append(card)
    accent = FancyBboxPatch(
        (x, 0.765),
        0.006,
        0.085,
        transform=fig.transFigure,
        boxstyle="round,pad=0,rounding_size=0.004",
        facecolor=color,
        edgecolor=color,
    )
    fig.patches.append(accent)
    fig.text(x + 0.010, 0.824, label, fontsize=7.2, color=MUTED, weight="medium")
    fig.text(x + 0.010, 0.785, value, fontsize=13.0, color=INK, weight="bold")


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

    sidebar = FancyBboxPatch(
        (0.018, 0.035),
        0.15,
        0.93,
        transform=fig.transFigure,
        boxstyle="round,pad=0.008,rounding_size=0.014",
        facecolor="#0B1739",
        edgecolor="#0B1739",
    )
    fig.patches.append(sidebar)
    avatar = FancyBboxPatch(
        (0.038, 0.885),
        0.038,
        0.054,
        transform=fig.transFigure,
        boxstyle="round,pad=0.004,rounding_size=0.010",
        facecolor=PURPLE,
        edgecolor="#8B5CF6",
    )
    fig.patches.append(avatar)
    fig.text(0.047, 0.903, "AA", fontsize=11, color=WHITE, weight="bold")
    fig.text(0.038, 0.855, "Aamir Husain Azad", fontsize=9.4, color=WHITE, weight="bold")
    fig.text(0.038, 0.835, "AI/ML & Data Analytics", fontsize=7.2, color="#BFD5FF")
    fig.text(0.038, 0.790, "DASHBOARD NAVIGATION", fontsize=6.8, color="#8FB7FF", weight="bold")
    nav_items = [
        ("Executive Overview", True),
        ("Customer Intelligence", False),
        ("Products & Returns", False),
        ("Data Quality", False),
        ("Project & Technology", False),
    ]
    for index, (label, selected) in enumerate(nav_items):
        y = 0.742 - index * 0.057
        nav = FancyBboxPatch(
            (0.033, y),
            0.119,
            0.040,
            transform=fig.transFigure,
            boxstyle="round,pad=0.004,rounding_size=0.007",
            facecolor=BLUE if selected else "#172B55",
            edgecolor="#4678CD" if selected else "#29436F",
            linewidth=0.8,
        )
        fig.patches.append(nav)
        fig.text(0.043, y + 0.013, label, fontsize=6.8, color=WHITE if selected else "#D9E5FF", weight="bold" if selected else "normal")
    fig.text(0.038, 0.420, "FILTERS", fontsize=6.8, color="#8FB7FF", weight="bold")
    for index, label in enumerate(["Date: Jan 2024–Dec 2025", "Region: All", "Category: All", "Channel: All"]):
        filter_box = FancyBboxPatch(
            (0.033, 0.373 - index * 0.050),
            0.119,
            0.035,
            transform=fig.transFigure,
            boxstyle="round,pad=0.003,rounding_size=0.006",
            facecolor="#F8FAFF",
            edgecolor="#D8E2F1",
        )
        fig.patches.append(filter_box)
        fig.text(0.041, 0.385 - index * 0.050, label, fontsize=6.3, color="#3E5578")
    fig.text(0.038, 0.160, "CONNECTED STACK", fontsize=6.8, color="#8FB7FF", weight="bold")
    fig.text(0.038, 0.130, "Python · SQL · Excel", fontsize=7.0, color="#E1EAFF")
    fig.text(0.038, 0.105, "Power BI · ML · Statistics", fontsize=7.0, color="#E1EAFF")
    fig.text(0.038, 0.069, "SCROLL  •  FILTER  •  EXPLORE", fontsize=6.1, color="#7DD3FC", weight="bold")

    hero = FancyBboxPatch(
        (0.19, 0.875),
        0.775,
        0.09,
        transform=fig.transFigure,
        boxstyle="round,pad=0.008,rounding_size=0.014",
        facecolor=NAVY,
        edgecolor=NAVY,
    )
    fig.patches.append(hero)
    fig.text(0.212, 0.929, "Retail Sales & Customer Insights", fontsize=22, color=WHITE, weight="bold")
    fig.text(
        0.212,
        0.903,
        "Connected browser dashboard · 1 Jan 2024–31 Dec 2025 · Synthetic portfolio data",
        fontsize=9.6,
        color="#DCE6F8",
    )
    fig.text(0.765, 0.921, "Built by Aamir Husain Azad", fontsize=9, color=WHITE, weight="bold")
    fig.text(0.765, 0.898, "AI/ML & Data Analytics Portfolio", fontsize=7.8, color="#BFD5FF")

    cards = [
        ("Revenue", f"₹{kpis['revenue'] / 1_000_000:.1f}M"),
        ("Profit", f"₹{kpis['profit'] / 1_000_000:.1f}M"),
        ("Profit Margin", f"{kpis['profit_margin']:.1%}"),
        ("Orders", f"{kpis['orders']:,}"),
        ("Customers", f"{kpis['customers']:,}"),
        ("Return Rate", f"{kpis['return_rate']:.1%}"),
        ("Avg Order Value", f"₹{kpis['average_order_value']:,.0f}"),
    ]
    for index, (label, value) in enumerate(cards):
        add_card(fig, 0.195 + index * 0.110, label, value, PALETTE[index])

    grid = fig.add_gridspec(2, 2, left=0.205, right=0.955, bottom=0.09, top=0.69, hspace=0.40, wspace=0.25)

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
    category_colors = [BLUE, PURPLE, CYAN, GOLD, PINK][: len(ranked)]
    bars = ax.barh(ranked["category"], ranked["revenue"] / 1_000_000, color=category_colors, edgecolor=WHITE)
    style_axis(ax, "Revenue by Product Category", "INR million · all validated transactions")
    ax.set_xlabel("₹ million", color=MUTED, fontsize=9)
    ax.bar_label(bars, labels=[f"{value:.1f}" for value in ranked["revenue"] / 1_000_000], padding=4, fontsize=8, color=INK)
    ax.set_xlim(0, (ranked["revenue"].max() / 1_000_000) * 1.14)

    ax = fig.add_subplot(grid[1, 0])
    ax.bar(x, monthly["target_revenue"] / 1_000_000, color="#DCE6F8", edgecolor="#9DB7E4", label="Target")
    ax.plot(x, monthly["revenue"] / 1_000_000, color=PURPLE, linewidth=2.2, marker="o", markersize=3.8, label="Actual")
    style_axis(ax, "Monthly Revenue versus Target", "INR million · actual sales compared with monthly plan")
    ax.set_xticks(x[::2], monthly["year_month"].iloc[::2], rotation=45, ha="right")
    ax.set_ylabel("₹ million", color=MUTED, fontsize=9)
    ax.legend(frameon=False, loc="upper left", ncol=2, fontsize=8.5)

    ax = fig.add_subplot(grid[1, 1])
    returns = category.sort_values("return_rate")
    return_colors = ["#FDBA74", "#FB923C", ORANGE, PINK, PURPLE][: len(returns)]
    bars = ax.barh(returns["category"], returns["return_rate"] * 100, color=return_colors, edgecolor=WHITE)
    style_axis(ax, "Order Return Rate by Category", "Returned distinct orders ÷ distinct orders")
    ax.set_xlabel("% of orders", color=MUTED, fontsize=9)
    ax.bar_label(bars, labels=[f"{value:.1%}" for value in returns["return_rate"]], padding=4, fontsize=8, color=INK)
    ax.set_xlim(0, returns["return_rate"].max() * 100 * 1.18)

    fig.text(
        0.205,
        0.035,
        "Source: data/database/retail_analytics.db · Grain: one row per validated order line · 4,180 lines · 15/15 quality checks passed",
        fontsize=8.5,
        color=MUTED,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def render_products_page(output_path: Path) -> None:
    transactions = load_transactions(PROJECT_ROOT / "data" / "database" / "retail_analytics.db")
    kpis = calculate_kpis(transactions)
    category = category_performance(transactions)
    products = top_products(transactions, limit=8).sort_values("revenue")
    collection_image = plt.imread(PROJECT_ROOT / "assets" / "retail-product-collection.png")

    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titleweight": "bold"})
    fig = plt.figure(figsize=(16, 10.5), facecolor=PAGE)

    sidebar = FancyBboxPatch(
        (0.018, 0.035), 0.15, 0.93, transform=fig.transFigure,
        boxstyle="round,pad=0.008,rounding_size=0.014", facecolor="#101A42", edgecolor="#101A42",
    )
    fig.patches.append(sidebar)
    avatar = FancyBboxPatch(
        (0.038, 0.885), 0.038, 0.054, transform=fig.transFigure,
        boxstyle="round,pad=0.004,rounding_size=0.010", facecolor=PURPLE, edgecolor="#8B5CF6",
    )
    fig.patches.append(avatar)
    fig.text(0.047, 0.903, "AA", fontsize=11, color=WHITE, weight="bold")
    fig.text(0.038, 0.855, "Aamir Husain Azad", fontsize=9.4, color=WHITE, weight="bold")
    fig.text(0.038, 0.835, "AI/ML & Data Analytics", fontsize=7.2, color="#BFD5FF")
    fig.text(0.038, 0.790, "DASHBOARD NAVIGATION", fontsize=6.8, color="#8FB7FF", weight="bold")
    nav_items = ["Executive Overview", "Customer Intelligence", "Products & Returns", "Data Quality", "Project & Technology"]
    for index, label in enumerate(nav_items):
        selected = label == "Products & Returns"
        y = 0.742 - index * 0.057
        nav = FancyBboxPatch(
            (0.033, y), 0.119, 0.040, transform=fig.transFigure,
            boxstyle="round,pad=0.004,rounding_size=0.007",
            facecolor=BLUE if selected else "#1C356B", edgecolor="#5D8DE3" if selected else "#31518B", linewidth=0.8,
        )
        fig.patches.append(nav)
        fig.text(0.043, y + 0.013, label, fontsize=6.8, color=WHITE, weight="bold" if selected else "normal")

    fig.text(0.038, 0.420, "VISIBLE FEATURES", fontsize=6.8, color="#8FB7FF", weight="bold")
    features = ["Visual category gallery", "Return & discount risk", "Top-product cards", "50-product browser", "Connected downloads"]
    for index, label in enumerate(features):
        fig.text(0.042, 0.385 - index * 0.044, f"•  {label}", fontsize=7.0, color="#E1EAFF")
    fig.text(0.038, 0.120, "LOCAL PRODUCT IMAGE", fontsize=6.8, color="#8FB7FF", weight="bold")
    fig.text(0.038, 0.091, "Offline-ready · no broken links", fontsize=7.0, color="#E1EAFF")
    fig.text(0.038, 0.060, "SCROLL  •  FILTER  •  EXPLORE", fontsize=6.1, color="#7DD3FC", weight="bold")

    hero = FancyBboxPatch(
        (0.19, 0.875), 0.775, 0.09, transform=fig.transFigure,
        boxstyle="round,pad=0.008,rounding_size=0.014", facecolor=NAVY, edgecolor=NAVY,
    )
    fig.patches.append(hero)
    fig.text(0.212, 0.929, "Products & Returns Intelligence", fontsize=22, color=WHITE, weight="bold")
    fig.text(0.212, 0.903, "Visual product discovery · performance · return risk · complete catalog", fontsize=9.4, color="#DCE6F8")
    fig.text(0.79, 0.921, "5 categories · 50 products", fontsize=9, color=WHITE, weight="bold")
    fig.text(0.79, 0.898, "4,180 validated order lines", fontsize=7.8, color="#BFD5FF")

    cards = [
        ("Revenue", f"₹{kpis['revenue'] / 1_000_000:.1f}M"), ("Profit", f"₹{kpis['profit'] / 1_000_000:.1f}M"),
        ("Profit Margin", f"{kpis['profit_margin']:.1%}"), ("Orders", f"{kpis['orders']:,}"),
        ("Customers", f"{kpis['customers']:,}"), ("Return Rate", f"{kpis['return_rate']:.1%}"),
        ("Avg Order Value", f"₹{kpis['average_order_value']:,.0f}"),
    ]
    for index, (label, value) in enumerate(cards):
        add_card(fig, 0.195 + index * 0.110, label, value, PALETTE[index])

    image_ax = fig.add_axes([0.205, 0.365, 0.47, 0.355])
    image_ax.imshow(collection_image)
    image_ax.set_title("Visual Product Gallery", loc="left", fontsize=13, color=INK, pad=12, weight="bold")
    image_ax.text(0, 1.015, "Local generated asset covering all five retail categories", transform=image_ax.transAxes, fontsize=8.5, color=MUTED)
    image_ax.axis("off")

    category_icons = {"Electronics":"TECH", "Home & Kitchen":"HOME", "Sports & Outdoors":"SPORT", "Fashion":"STYLE", "Beauty & Personal Care":"CARE"}
    category_colors = {"Electronics":BLUE, "Home & Kitchen":GOLD, "Sports & Outdoors":CYAN, "Fashion":PURPLE, "Beauty & Personal Care":PINK}
    for index, row in enumerate(category.itertuples(index=False)):
        y = 0.652 - index * 0.070
        card = FancyBboxPatch(
            (0.70, y), 0.25, 0.055, transform=fig.transFigure,
            boxstyle="round,pad=0.005,rounding_size=0.009", facecolor=WHITE, edgecolor="#D9E4F3", linewidth=0.9,
        )
        fig.patches.append(card)
        fig.patches.append(FancyBboxPatch((0.70, y), 0.005, 0.055, transform=fig.transFigure, boxstyle="round,pad=0", facecolor=category_colors[row.category], edgecolor=category_colors[row.category]))
        fig.text(0.715, y + 0.034, row.category, fontsize=8.0, color=INK, weight="bold")
        fig.text(0.715, y + 0.014, f"{category_icons[row.category]}  ·  ₹{row.revenue / 1_000_000:.1f}M  ·  Margin {row.profit_margin:.1%}  ·  Returns {row.return_rate:.1%}", fontsize=6.7, color=MUTED)

    ax = fig.add_axes([0.245, 0.075, 0.705, 0.205])
    product_colors = [BLUE, PURPLE, CYAN, GOLD, ORANGE, OLIVE, PINK, BLUE]
    bars = ax.barh(products["product_name"], products["revenue"] / 1_000_000, color=product_colors[:len(products)], edgecolor=WHITE)
    style_axis(ax, "Top Products by Revenue", "INR million · eight highest-value products · exact catalog available in the live dashboard")
    ax.set_xlabel("₹ million", color=MUTED, fontsize=9)
    ax.bar_label(bars, fmt="%.1f", padding=4, fontsize=7.5, color=INK)
    ax.set_xlim(0, products["revenue"].max() / 1_000_000 * 1.16)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    render(PROJECT_ROOT / "reports" / "streamlit_dashboard_preview.png")
    render_products_page(PROJECT_ROOT / "reports" / "products_page_preview.png")
