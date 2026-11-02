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

from streamlit_app.dashboard_data import (  # noqa: E402
    apply_filters,
    business_segment_performance,
    calculate_kpis,
    category_performance,
    customer_ml_clusters,
    customer_segment_summary,
    discount_band_performance,
    has_scope_filters,
    load_quality_checks,
    load_quality_summary,
    load_transactions,
    monthly_performance,
    statistical_snapshot,
    top_products,
)
from streamlit_app.formatting import CRORE, LAKH, count, inr, inr_compact, month_label, pct  # noqa: E402
from streamlit_app.ui_helpers import (  # noqa: E402
    BLUE,
    CYAN,
    GOLD,
    INK,
    OLIVE,
    ORANGE,
    PALETTE,
    PINK,
    PURPLE,
    category_gallery_cards,
    chart_style,
    inject_dashboard_css,
    insight_cards,
    kpi_cards,
    pipeline_steps,
    read_download_bytes,
    render_back_to_top,
    render_footer,
    render_hero,
    scroll_menu,
    section_heading,
    technology_cards,
)


st.set_page_config(
    page_title="Retail Sales & Customer Insights",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto",
)

DATABASE_PATH = PROJECT_ROOT / "data" / "database" / "retail_analytics.db"
EXCEL_PATH = PROJECT_ROOT / "excel" / "Retail_Sales_Customer_Insights_Dashboard.xlsx"
DAX_PATH = PROJECT_ROOT / "power_bi" / "dax" / "Measures.dax"
POWER_QUERY_PATH = PROJECT_ROOT / "power_bi" / "power_query" / "Load_Star_Schema.m"
QUALITY_REPORT_PATH = PROJECT_ROOT / "reports" / "data_quality_report.md"
PRODUCT_COLLECTION_IMAGE = PROJECT_ROOT / "assets" / "retail-product-collection.png"
PORTFOLIO_URL = "https://aamir-ai-ml-portfolio.aamirhussainazad786.chatgpt.site/"
GITHUB_URL = "https://github.com/Aamiruem"

inject_dashboard_css()


@st.cache_data(show_spinner=False)
def cached_transactions(path: str) -> pd.DataFrame:
    return load_transactions(path)


@st.cache_data(show_spinner=False)
def cached_quality(project_root: str) -> pd.DataFrame:
    return load_quality_checks(project_root)


@st.cache_data(show_spinner=False)
def cached_quality_summary(project_root: str) -> dict:
    return load_quality_summary(project_root)


def format_inr_millions(value: float) -> str:
    """Kept for backwards compatibility; the dashboard now uses ₹ lakh / crore."""
    return inr_compact(value)


def show_table(frame: pd.DataFrame, column_config: dict, height: int | None = None) -> None:
    """Consistent, index-free, sortable table with human-readable headers."""
    frame = frame[list(column_config)].copy()
    for name, config in column_config.items():
        # Rupee amounts: whole rupees read better than paise in a dashboard.
        if (config.get("type_config") or {}).get("format") == "localized":
            frame[name] = frame[name].round(0)
    st.dataframe(
        frame,
        column_config=column_config,
        hide_index=True,
        width="stretch",
        height=height if height is not None else "auto",
    )


def monthly_axis(ax, labels) -> None:
    """Readable month axis: 'Jan 24' labels, every other month on dense charts."""
    positions = np.arange(len(labels))
    step = 2 if len(labels) > 14 else 1
    ax.set_xticks(positions[::step], [month_label(label) for label in list(labels)[::step]], rotation=0, fontsize=7.5)


def reset_filters(minimum_date, maximum_date) -> None:
    st.session_state["filter_dates"] = (minimum_date, maximum_date)
    st.session_state["filter_regions"] = []
    st.session_state["filter_categories"] = []
    st.session_state["filter_channels"] = []
    st.session_state["filter_segments"] = []


def render_sidebar(data: pd.DataFrame):
    minimum_date = data["order_date"].min().date()
    maximum_date = data["order_date"].max().date()
    filter_defaults = {
        "filter_dates": (minimum_date, maximum_date),
        "filter_regions": [],
        "filter_categories": [],
        "filter_channels": [],
        "filter_segments": [],
    }
    for key, value in filter_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
              <div class="initials">AA</div>
              <div><h4>Aamir Husain Azad</h4><p>AI/ML &amp; Data Analytics Portfolio</p></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("### Dashboard")
        page = st.radio(
            "Dashboard navigation",
            [
                "📈 Executive Overview",
                "👥 Customer Intelligence",
                "🛍️ Products & Returns",
                "🛡️ Data Quality",
                "🧰 Project & Technology",
            ],
            label_visibility="collapsed",
            key="dashboard_page",
        )

        st.markdown("### Filters")
        with st.expander("🎛️ Sales & customer filters", expanded=True):
            selected_dates = st.date_input(
                "Order date",
                min_value=minimum_date,
                max_value=maximum_date,
                key="filter_dates",
            )
            # While the user has picked only a start date, show that single day.
            if not isinstance(selected_dates, (tuple, list)) or len(selected_dates) == 0:
                selected_dates = (minimum_date, maximum_date)
            elif len(selected_dates) == 1:
                selected_dates = (selected_dates[0], selected_dates[0])

            selected_regions = st.multiselect(
                "Region", sorted(data["region"].unique()), key="filter_regions", placeholder="All regions"
            )
            selected_categories = st.multiselect(
                "Product category", sorted(data["category"].unique()), key="filter_categories", placeholder="All categories"
            )
            selected_channels = st.multiselect(
                "Sales channel", sorted(data["channel"].unique()), key="filter_channels", placeholder="All channels"
            )
            selected_segments = st.multiselect(
                "Customer segment",
                sorted(data["customer_segment"].unique()),
                key="filter_segments",
                placeholder="All customer segments",
            )

            active_filter_count = sum(
                bool(value) for value in [selected_regions, selected_categories, selected_channels, selected_segments]
            )
            st.markdown(
                f"""
                <div class="filter-summary">
                  <strong>Active scope</strong><br>
                  {selected_dates[0].strftime('%d %b %Y')} → {selected_dates[1].strftime('%d %b %Y')}<br>
                  {"All regions, categories, channels &amp; segments" if not active_filter_count else f"{active_filter_count} filter group{'s' if active_filter_count > 1 else ''} applied"}
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.button(
                "↻ Reset filters",
                width="stretch",
                on_click=reset_filters,
                args=(minimum_date, maximum_date),
            )

        with st.expander("🔗 Portfolio & GitHub"):
            st.link_button("🌐 Open Portfolio", PORTFOLIO_URL, width="stretch")
            st.link_button("💻 Open GitHub Profile", GITHUB_URL, width="stretch")
        st.markdown(
            f'<p class="sidebar-note">{count(len(data))} validated order lines · Amounts in ₹ · Synthetic data</p>',
            unsafe_allow_html=True,
        )

    return (
        page,
        selected_dates,
        selected_regions,
        selected_categories,
        selected_channels,
        selected_segments,
    )


def render_kpis(data: pd.DataFrame) -> dict[str, float | int]:
    kpis = calculate_kpis(data)
    kpi_cards(
        [
            ("Revenue", inr_compact(kpis["revenue"]), "After discounts & returns", "💰", BLUE),
            ("Profit", inr_compact(kpis["profit"]), "Revenue minus cost", "📈", PURPLE),
            ("Margin", pct(kpis["profit_margin"]), "Profit ÷ revenue", "🎯", CYAN),
            ("Orders", count(kpis["orders"]), "Distinct orders", "🧾", GOLD),
            ("Customers", count(kpis["customers"]), "Unique buyers", "👥", ORANGE),
            ("Return rate", pct(kpis["return_rate"]), "Orders with a return", "↩️", OLIVE),
            ("Avg order", inr(kpis["average_order_value"]), "Revenue ÷ orders", "🛒", PINK),
        ]
    )
    return kpis


def render_overview(data: pd.DataFrame, scoped: bool = False) -> None:
    monthly = monthly_performance(data)
    category = category_performance(data)
    best_category = category.iloc[0]
    best_region = data.groupby("region")["revenue"].sum().idxmax()
    best_month = monthly.loc[monthly["revenue"].idxmax()]
    target_attainment = monthly["revenue"].sum() / monthly["target_revenue"].sum()

    scroll_menu(
        [
            ("overview-summary", "Summary"),
            ("overview-trends", "Trends"),
            ("overview-targets", "Targets & Mix"),
            ("downloads", "Downloads"),
        ]
    )
    section_heading(
        "Executive Overview",
        "Performance, momentum, target delivery and the strongest revenue drivers.",
        "📈",
        "overview-summary",
    )
    insight_cards(
        [
            ("Top category", str(best_category["category"]), f"{inr_compact(best_category['revenue'])} revenue", BLUE),
            ("Top region", str(best_region), f"{inr_compact(data.loc[data['region'].eq(best_region), 'revenue'].sum())} revenue", PURPLE),
            ("Best month", month_label(best_month["year_month"]).replace(" ", " 20"), f"{inr_compact(best_month['revenue'])} revenue", CYAN),
            (
                "Target attainment",
                "Company only" if scoped else pct(target_attainment),
                "Targets are set for the whole company" if scoped else "Actual revenue ÷ target",
                GOLD,
            ),
        ]
    )

    section_heading("Performance Trends", "Monthly momentum and category contribution.", "📊", "overview-trends")
    left, right = st.columns([1.35, 1])
    with left:
        x = np.arange(len(monthly))
        fig, ax = plt.subplots(figsize=(9.3, 4.3))
        ax.fill_between(x, monthly["revenue"] / LAKH, color=BLUE, alpha=0.08)
        ax.plot(x, monthly["revenue"] / LAKH, color=BLUE, linewidth=2.4, marker="o", markersize=4, label="Revenue")
        ax.plot(x, monthly["profit"] / LAKH, color=GOLD, linewidth=2.2, marker="o", markersize=4, label="Profit")
        chart_style(ax, "Monthly revenue and profit", "₹ lakh per month", ylabel="₹ lakh")
        monthly_axis(ax, monthly["year_month"])
        ax.set_ylim(bottom=0)
        ax.legend(frameon=False, ncol=2, loc="upper left")
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    with right:
        ordered = category.sort_values("revenue")
        fig, ax = plt.subplots(figsize=(7.3, 4.3))
        # Highlight the leading category; the rest stay in a lighter tint.
        colors = ["#93C5FD"] * (len(ordered) - 1) + [BLUE]
        bars = ax.barh(ordered["category"], ordered["revenue"] / CRORE, color=colors, height=0.6)
        chart_style(ax, "Revenue by category", "₹ crore · share of filtered revenue", xlabel="₹ crore")
        total = ordered["revenue"].sum()
        ax.bar_label(
            bars,
            labels=[f"₹{value / CRORE:.2f} Cr  ({value / total:.0%})" for value in ordered["revenue"]],
            padding=4,
            fontsize=8,
            color=INK,
        )
        ax.set_xlim(0, ordered["revenue"].max() / CRORE * 1.35)
        ax.grid(axis="y", visible=False)
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)

    section_heading(
        "Targets & Geographic Mix",
        "Plan delivery and the region × category combinations driving revenue.",
        "🎯",
        "overview-targets",
    )
    if scoped:
        st.markdown(
            '<div class="note warn">Monthly targets are company-wide. With region, category, channel or segment '
            "filters applied, the target bars are shown for context only.</div>",
            unsafe_allow_html=True,
        )
    left, right = st.columns([1.35, 1])
    with left:
        fig, ax = plt.subplots(figsize=(9.3, 4.2))
        x = np.arange(len(monthly))
        attained = monthly["revenue"] >= monthly["target_revenue"]
        ax.bar(x, monthly["target_revenue"] / LAKH, color="#E2E8F0", label="Target", width=0.7)
        ax.plot(x, monthly["revenue"] / LAKH, color=PURPLE, linewidth=2.2, label="Actual")
        ax.scatter(x[attained], (monthly["revenue"] / LAKH)[attained], color=OLIVE, s=26, zorder=3, label="Target met")
        ax.scatter(x[~attained], (monthly["revenue"] / LAKH)[~attained], color=ORANGE, s=26, zorder=3, label="Below target")
        monthly_axis(ax, monthly["year_month"])
        chart_style(ax, "Monthly revenue versus target", "₹ lakh · green = target met, orange = below target", ylabel="₹ lakh")
        ax.legend(frameon=False, ncol=4, loc="upper left")
        ax.set_ylim(0, max(monthly["target_revenue"].max(), monthly["revenue"].max()) / LAKH * 1.18)
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    with right:
        heat = data.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum", fill_value=0) / LAKH
        heat.columns = [str(column).replace(" & ", " &\n") for column in heat.columns]
        fig, ax = plt.subplots(figsize=(7.3, 4.2))
        cmap = sns.light_palette(BLUE, as_cmap=True)
        sns.heatmap(
            heat,
            annot=True,
            fmt=".0f",
            cmap=cmap,
            linewidths=1.5,
            linecolor="#FFFFFF",
            cbar=False,
            annot_kws={"fontsize": 8.5, "fontweight": "bold"},
            ax=ax,
        )
        chart_style(ax, "Revenue by region and category", "₹ lakh · darker cells earn more")
        ax.grid(False)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(axis="x", rotation=0, labelsize=7.5)
        ax.tick_params(axis="y", rotation=0)
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)


def render_customer_360(data: pd.DataFrame) -> None:
    profile, ml_summary = customer_ml_clusters(data)
    rfm = customer_segment_summary(data)
    business_segments = business_segment_performance(data)
    champions = int(profile.loc[profile["rfm_segment"].eq("Champions"), "customer_id"].nunique())
    at_risk = int(profile.loc[profile["rfm_segment"].eq("At Risk"), "customer_id"].nunique())

    scroll_menu(
        [
            ("customer-summary", "Summary"),
            ("customer-rfm", "RFM"),
            ("customer-ml", "ML Clusters"),
            ("customer-value", "Value"),
            ("downloads", "Downloads"),
        ]
    )
    section_heading(
        "Customer Intelligence",
        "Understand value, lifecycle position, behavior and the best next action for every customer group.",
        "👥",
        "customer-summary",
    )
    insight_cards(
        [
            ("Active customers", f"{len(profile):,}", "Unique customers in scope", BLUE),
            ("Champions", f"{champions:,}", "Highest-value RFM group", OLIVE),
            ("At-risk customers", f"{at_risk:,}", "Retention opportunity", ORANGE),
            ("Revenue per customer", inr(profile["revenue"].mean()), "Average customer value", PINK),
        ]
    )

    section_heading(
        "RFM Lifecycle Segmentation",
        "Recency, frequency and monetary scoring translates transaction history into practical retention groups.",
        "🧭",
        "customer-rfm",
    )
    left, right = st.columns([1, 1.25])
    with left:
        ordered = rfm.sort_values("customers")
        segment_names = sorted(profile["rfm_segment"].unique())
        segment_colors = {name: PALETTE[index % len(PALETTE)] for index, name in enumerate(segment_names)}
        fig, ax = plt.subplots(figsize=(7.2, 5.0))
        bars = ax.barh(
            ordered["rfm_segment"], ordered["customers"], color=[segment_colors[name] for name in ordered["rfm_segment"]], height=0.62
        )
        chart_style(ax, "Customers by RFM segment", "Unique customers in each lifecycle group", xlabel="Customers")
        ax.bar_label(bars, padding=4, fontsize=8, color=INK)
        ax.grid(axis="y", visible=False)
        ax.set_xlim(0, ordered["customers"].max() * 1.15)
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    with right:
        # One bubble per segment is far easier to read than 1,000+ overlapping points.
        segments = profile.groupby("rfm_segment", as_index=False).agg(
            customers=("customer_id", "nunique"),
            recency_days=("recency_days", "mean"),
            orders=("orders", "mean"),
            revenue=("revenue", "mean"),
        )
        fig, ax = plt.subplots(figsize=(8.7, 5.0))
        ax.scatter(
            segments["recency_days"],
            segments["revenue"] / 1_000,
            s=segments["customers"] / segments["customers"].max() * 1800 + 120,
            c=[segment_colors[name] for name in segments["rfm_segment"]],
            alpha=0.78,
            edgecolors="#FFFFFF",
            linewidths=1.5,
        )
        for row in segments.itertuples(index=False):
            ax.annotate(
                f"{row.rfm_segment}\n{row.customers} customers",
                (row.recency_days, row.revenue / 1_000),
                ha="center",
                va="center",
                fontsize=7.5,
                color=INK,
                fontweight="bold",
            )
        chart_style(
            ax,
            "Segment value versus recency",
            "Bubble size = customers · left = bought recently, up = spends more",
            ylabel="Avg revenue per customer (₹ thousand)",
            xlabel="Avg days since last order",
        )
        ax.margins(x=0.18, y=0.22)
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)

    section_heading(
        "Machine Learning Customer Clusters",
        "K-Means groups customers by recency, order frequency and revenue after scaling and log transformation.",
        "🤖",
        "customer-ml",
    )
    cluster_colors = {
        "High Value": OLIVE,
        "Loyal Growth": BLUE,
        "Developing": GOLD,
        "Needs Attention": ORANGE,
        "Single Active Group": PURPLE,
    }
    left, right = st.columns([1.3, 1])
    with left:
        plot_profile = profile.assign(revenue_thousands=profile["revenue"] / 1_000)
        active_cluster_colors = {
            cluster: cluster_colors.get(cluster, PALETTE[index % len(PALETTE)])
            for index, cluster in enumerate(sorted(plot_profile["ml_cluster"].unique()))
        }
        fig, ax = plt.subplots(figsize=(8.7, 4.9))
        sns.scatterplot(
            data=plot_profile,
            x="recency_days",
            y="revenue_thousands",
            hue="ml_cluster",
            size="orders",
            sizes=(30, 150),
            palette=active_cluster_colors,
            alpha=0.74,
            edgecolor="#FFFFFF",
            linewidth=0.45,
            ax=ax,
        )
        chart_style(
            ax,
            "ML Customer Map",
            "One point per customer · larger points represent more orders",
            ylabel="Customer revenue (₹ thousand)",
            xlabel="Recency (days)",
        )
        handles, labels = ax.get_legend_handles_labels()
        keep = [index for index, label in enumerate(labels) if label in active_cluster_colors]
        ax.legend([handles[index] for index in keep], [labels[index] for index in keep], frameon=False, title="Cluster", loc="upper right")
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    with right:
        ordered_ml = ml_summary.sort_values("average_revenue")
        bar_colors = [cluster_colors.get(name, PURPLE) for name in ordered_ml["ml_cluster"]]
        fig, ax = plt.subplots(figsize=(7.2, 4.9))
        bars = ax.barh(ordered_ml["ml_cluster"], ordered_ml["average_revenue"] / 1_000, color=bar_colors, height=0.6)
        ax.grid(axis="y", visible=False)
        chart_style(
            ax,
            "Average Value by ML Cluster",
            "Mean customer revenue within each behavioral group",
            xlabel="Average revenue (₹ thousand)",
        )
        ax.bar_label(bars, fmt="₹%.0fK", padding=4, fontsize=8, color=INK)
        ax.set_xlim(0, ordered_ml["average_revenue"].max() / 1_000 * 1.22)
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)

    cluster_table = ml_summary.assign(profit_margin=ml_summary["profit_margin"].map(pct))
    show_table(
        cluster_table,
        {
            "ml_cluster": st.column_config.TextColumn("Customer cluster"),
            "customers": st.column_config.NumberColumn("Customers", format="%d"),
            "average_recency_days": st.column_config.NumberColumn("Avg recency (days)", format="%.0f"),
            "average_orders": st.column_config.NumberColumn("Avg orders", format="%.1f"),
            "average_revenue": st.column_config.NumberColumn("Avg revenue (₹)", format="localized"),
            "total_revenue": st.column_config.NumberColumn("Total revenue (₹)", format="localized"),
            "profit_margin": st.column_config.TextColumn("Profit margin", help="— when the group has no net revenue"),
        },
    )
    st.info(
        "**Action guide:** reward High Value customers, cross-sell to Loyal Growth, nurture Developing customers and run win-back campaigns for Needs Attention. Cluster labels are exploratory, not predictions.",
        icon="💡",
    )

    section_heading(
        "Customer Value & Leaderboard",
        "Compare business segments and inspect the highest-value individual customers.",
        "💎",
        "customer-value",
    )
    left, right = st.columns([1, 1.25])
    with left:
        ordered = business_segments.sort_values("revenue")
        y = np.arange(len(ordered))
        fig, ax = plt.subplots(figsize=(7.2, 4.5))
        ax.barh(y + 0.18, ordered["revenue"] / LAKH, height=0.34, color=BLUE, label="Revenue")
        ax.barh(y - 0.18, ordered["profit"] / LAKH, height=0.34, color=GOLD, label="Profit")
        ax.grid(axis="y", visible=False)
        ax.set_yticks(y, ordered["customer_segment"])
        chart_style(ax, "Value by customer segment", "₹ lakh · revenue and profit", xlabel="₹ lakh")
        ax.legend(frameon=False, ncol=2, loc="lower right")
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    with right:
        top_customers = profile.head(15).copy()
        top_customers.insert(0, "rank", range(1, len(top_customers) + 1))
        st.markdown("**🏆 Top 15 customers by revenue**")
        show_table(
            top_customers,
            {
                "rank": st.column_config.NumberColumn("#", format="%d", width="small"),
                "customer_name": st.column_config.TextColumn("Customer"),
                "rfm_segment": st.column_config.TextColumn("RFM segment"),
                "ml_cluster": st.column_config.TextColumn("Cluster"),
                "revenue": st.column_config.NumberColumn("Revenue (₹)", format="localized"),
                "orders": st.column_config.NumberColumn("Orders", format="%d"),
                "last_order": st.column_config.DateColumn("Last order", format="DD MMM YYYY"),
            },
            height=420,
        )


def render_products(data: pd.DataFrame) -> None:
    category = category_performance(data)
    all_products = top_products(data, limit=50)
    products = all_products.head(12).copy()
    top_product = products.iloc[0]
    high_return_category = category.loc[category["return_rate"].idxmax()]

    scroll_menu(
        [
            ("product-summary", "Summary"),
            ("product-gallery", "Visual Gallery"),
            ("product-risk", "Return & Discount Risk"),
            ("product-leaders", "Products"),
            ("product-catalog", "Full Catalog"),
            ("downloads", "Downloads"),
        ]
    )
    section_heading(
        "Products & Returns",
        "Compare product contribution, promotion depth, profitability and return risk.",
        "🛍️",
        "product-summary",
    )
    insight_cards(
        [
            ("Top product", str(top_product["product_name"]), f"{inr_compact(top_product['revenue'])} revenue", BLUE),
            ("Top-product margin", pct(top_product["profit_margin"]), "Profit ÷ revenue", OLIVE),
            ("Highest return rate", str(high_return_category["category"]), f"{pct(high_return_category['return_rate'])} of orders", ORANGE),
            ("Units sold", count(data["quantity"].sum()), "Across filtered order lines", PURPLE),
        ]
    )

    section_heading(
        "Visual Product Gallery",
        "A quick visual guide to the five product families represented in the retail model.",
        "🖼️",
        "product-gallery",
    )
    if PRODUCT_COLLECTION_IMAGE.exists():
        st.image(
            str(PRODUCT_COLLECTION_IMAGE),
            caption="Representative collection covering Electronics, Home & Kitchen, Sports & Outdoors, Fashion, and Beauty & Personal Care.",
            width="stretch",
        )
    else:
        st.warning("The local product collection image is unavailable. The analytical product views remain active.")

    category_icons = {
        "Electronics": "💻",
        "Home & Kitchen": "🏠",
        "Sports & Outdoors": "⚽",
        "Fashion": "👟",
        "Beauty & Personal Care": "🧴",
    }
    category_colors = {
        "Electronics": BLUE,
        "Home & Kitchen": GOLD,
        "Sports & Outdoors": CYAN,
        "Fashion": PURPLE,
        "Beauty & Personal Care": PINK,
    }
    category_gallery_cards(
        [
            (
                category_icons.get(str(row.category), "🛍️"),
                str(row.category),
                inr_compact(row.revenue),
                f"Margin {pct(row.profit_margin)} · Returns {pct(row.return_rate)} · {count(row.orders)} orders",
                category_colors.get(str(row.category), BLUE),
            )
            for row in category.itertuples(index=False)
        ]
    )

    section_heading(
        "Return & Discount Risk",
        "Find categories with elevated returns and examine whether discount depth is eroding line profit.",
        "⚠️",
        "product-risk",
    )
    left, right = st.columns(2)
    with left:
        returns = category.sort_values("return_rate")
        overall_rate = calculate_kpis(data)["return_rate"]
        colors = [ORANGE if rate > overall_rate else "#FDBA74" for rate in returns["return_rate"]]
        fig, ax = plt.subplots(figsize=(7.6, 4.7))
        bars = ax.barh(returns["category"], returns["return_rate"] * 100, color=colors, height=0.6)
        ax.axvline(overall_rate * 100, color=INK, linestyle="--", linewidth=1)
        ax.text(overall_rate * 100, len(returns) - 0.45, f" Avg {pct(overall_rate)}", fontsize=7.5, color=INK, va="bottom")
        ax.grid(axis="y", visible=False)
        chart_style(ax, "Return rate by category", "Orders with a return · dark bars are above average", xlabel="% of orders")
        ax.bar_label(bars, labels=[f"{value:.1%}" for value in returns["return_rate"]], padding=4, fontsize=8, color=INK)
        ax.set_xlim(0, returns["return_rate"].max() * 100 * 1.18)
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    with right:
        bands = discount_band_performance(data)
        x = np.arange(len(bands))
        fig, ax = plt.subplots(figsize=(7.6, 4.7))
        bars = ax.bar(x, bands["profit_margin"] * 100, color=BLUE, width=0.55, label="Profit margin")
        ax.bar_label(bars, labels=[pct(value) for value in bands["profit_margin"]], padding=3, fontsize=8, color=INK)
        twin = ax.twinx()
        twin.plot(x, bands["loss_share"] * 100, color=ORANGE, marker="o", linewidth=2.2, label="Loss-making lines")
        twin.set_ylim(0, max(5.0, float(np.nanmax(bands["loss_share"])) * 100 * 1.4))
        twin.set_ylabel("Loss-making lines (%)", color=ORANGE, fontsize=8.5)
        twin.tick_params(colors=ORANGE, labelsize=8, length=0)
        for spine in twin.spines.values():
            spine.set_visible(False)
        ax.set_xticks(x, bands["discount_band"].astype(str))
        chart_style(
            ax,
            "Does discounting erode profit?",
            "Bars = margin per discount band · line = share of lines sold at a loss",
            ylabel="Profit margin (%)",
            xlabel="Discount band",
        )
        ax.set_ylim(0, float(np.nanmax(bands["profit_margin"])) * 100 * 1.25)
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)

    section_heading(
        "Product Leaderboard",
        "The 12 highest-revenue products and the context behind each result.",
        "🏅",
        "product-leaders",
    )
    category_gallery_cards(
        [
            (
                category_icons.get(str(row.category), "📦"),
                str(row.product_name),
                inr_compact(row.revenue),
                f"{row.category} · Margin {pct(row.profit_margin)} · {count(row.units)} units · {count(row.returned_lines)} returns",
                category_colors.get(str(row.category), BLUE),
            )
            for row in products.itertuples(index=False)
        ]
    )

    section_heading(
        "Complete Product Catalog",
        "Pick a category to see every product, sortable by any column.",
        "📚",
        "product-catalog",
    )
    catalog_category = st.selectbox(
        "Browse products by category",
        sorted(all_products["category"].unique()),
        key="catalog_category",
    )
    catalog = all_products.loc[all_products["category"].eq(catalog_category)].copy()
    catalog.insert(0, "rank", range(1, len(catalog) + 1))
    st.markdown(
        f'<div class="catalog-note"><strong>{catalog_category}</strong> · {len(catalog)} products · sorted by revenue. '
        "Click a column header to re-sort.</div>",
        unsafe_allow_html=True,
    )
    show_table(catalog, {
            "rank": st.column_config.NumberColumn("#", format="%d", width="small"),
            "product_name": st.column_config.TextColumn("Product"),
            "revenue": st.column_config.NumberColumn("Revenue (₹)", format="localized"),
            "profit": st.column_config.NumberColumn("Profit (₹)", format="localized"),
            "profit_margin": st.column_config.ProgressColumn(
                "Profit margin", format="percent", min_value=0.0, max_value=0.6
            ),
            "units": st.column_config.NumberColumn("Units", format="%d"),
            "returned_lines": st.column_config.NumberColumn("Returns", format="%d"),
        })


def render_quality(data: pd.DataFrame) -> None:
    checks = cached_quality(str(PROJECT_ROOT))
    scroll_menu(
        [
            ("quality-summary", "Summary"),
            ("quality-checks", "Automated Checks"),
            ("downloads", "Downloads"),
        ]
    )
    section_heading(
        "Data Quality & Model Readiness",
        "Review validation coverage, rejected records, lineage and analytical deliverables.",
        "🛡️",
        "quality-summary",
    )
    summary = cached_quality_summary(str(PROJECT_ROOT))
    raw_rows = int(summary.get("raw_rows", 0))
    clean_rows = int(summary.get("clean_rows", len(data)))
    rejected_rows = int(summary.get("rejected_rows", max(raw_rows - clean_rows, 0)))
    passed = int(checks["passed"].sum())
    failed = len(checks) - passed
    kpi_cards(
        [
            ("Raw rows", count(raw_rows), "Loaded from 3 sources", "📥", BLUE),
            ("Validated rows", count(clean_rows), f"{pct(clean_rows / raw_rows if raw_rows else 0)} accepted", "✅", OLIVE),
            ("Rejected rows", count(rejected_rows), "Quarantined, not deleted", "🚫", ORANGE),
            ("Checks passed", f"{passed}/{len(checks)}", "All clear" if not failed else f"{failed} need attention", "🛡️", PURPLE),
            ("Status", str(summary.get("overall_status", "—")).title(), "Pipeline readiness", "🚦", CYAN),
        ]
    )
    rejections = summary.get("rejection_counts") or {}
    if rejections:
        reasons = " · ".join(f"{name.replace('_', ' ')}: {value}" for name, value in rejections.items())
        st.markdown(f'<div class="note">Rejected-row reasons — {reasons}</div>', unsafe_allow_html=True)
    section_heading(
        "Automated Quality Checks",
        "Volume, completeness, uniqueness, ranges, referential integrity and financial arithmetic.",
        "✅",
        "quality-checks",
    )
    show_table(
        checks,
        {
            "check_id": st.column_config.TextColumn("ID", width="small"),
            "check_name": st.column_config.TextColumn("Check"),
            "actual": st.column_config.NumberColumn("Actual", format="localized"),
            "expected": st.column_config.NumberColumn("Expected", format="localized"),
            "severity": st.column_config.TextColumn("Severity", width="small"),
            "status": st.column_config.TextColumn("Status", width="small"),
        },
    )
    st.info(
        "Dataset grain: one validated order line. The SQL star schema, Streamlit KPIs, Excel dashboard and Power BI measures use the same metric definitions."
    )


def render_project_stack(data: pd.DataFrame) -> None:
    stats = statistical_snapshot(data)
    scroll_menu(
        [
            ("project-workflow", "Workflow"),
            ("project-tools", "Tools"),
            ("project-statistics", "Statistics"),
            ("project-deliverables", "Deliverables"),
            ("downloads", "Downloads"),
        ]
    )
    section_heading(
        "End-to-End Analytics Project",
        "See how raw retail files become validated models, customer intelligence and connected business dashboards.",
        "🧰",
        "project-workflow",
    )
    pipeline_steps(
        [
            ("📁", "Source", "CSV, Excel and SQL inputs"),
            ("🐍", "Prepare", "Pandas and NumPy cleaning"),
            ("🗄️", "Model", "SQLite star schema"),
            ("📐", "Analyze", "KPIs and statistics"),
            ("🤖", "Segment", "RFM and K-Means ML"),
            ("📊", "Deliver", "Excel, Power BI and Streamlit"),
        ]
    )

    section_heading(
        "Tools & Technology",
        "Every technology has a working role in the project—from source preparation to executive delivery.",
        "⚙️",
        "project-tools",
    )
    technology_cards(
        [
            ("🐍", "Python Analytics", "Cleans, transforms and analyzes transactions through reusable modules.", "Python · Pandas · NumPy", BLUE),
            ("🗄️", "SQL & SQLite", "Stores a star schema and powers reusable KPI and customer queries.", "SQL · SQLite · Views", PURPLE),
            ("📗", "Excel Dashboard", "Provides formula-driven KPI cards, charts and a familiar business interface.", "Excel · Tables · Formulas", OLIVE),
            ("📊", "Power BI", "Includes a ready semantic model, Power Query pipeline and governed measures.", "Power BI · Power Query · DAX", GOLD),
            ("🤖", "Machine Learning", "Clusters customers using scaled recency, frequency and monetary behavior.", "scikit-learn · K-Means", CYAN),
            ("📐", "Statistics", "Summarizes distributions, uncertainty and discount-profit relationships.", "Correlation · CI · Dispersion", ORANGE),
            ("🌐", "Browser Dashboard", "Connects filters, customer views, downloads and portfolio links.", "Streamlit · Matplotlib · Seaborn", PINK),
            ("✅", "Quality Engineering", "Validates volume, completeness, keys, ranges, joins and arithmetic.", "Automated tests · Data dictionary", BLUE),
        ]
    )

    section_heading(
        "Statistics Lab",
        "Use descriptive statistics and uncertainty to interpret customer and promotion behavior responsibly.",
        "📐",
        "project-statistics",
    )
    correlation = float(stats["discount_profit_correlation"])
    correlation_text = "N/A" if np.isnan(correlation) else f"{correlation:+.2f}"
    insight_cards(
        [
            ("Discount ↔ profit", correlation_text, "Pearson line-level correlation", ORANGE),
            ("Average discount", pct(stats["average_discount"]), "Mean promotional depth", BLUE),
            ("Median line revenue", inr(stats["line_revenue_median"]), "Typical order-line value", PURPLE),
            (
                "Return-rate interval",
                f"{pct(stats['return_rate_ci_low'])} – {pct(stats['return_rate_ci_high'])}",
                "Approximate 95% confidence interval",
                OLIVE,
            ),
        ]
    )

    left, right = st.columns(2)
    with left:
        fig, ax = plt.subplots(figsize=(7.8, 4.7))
        sns.histplot(data["revenue"] / 1_000, bins=28, color=BLUE, alpha=0.82, edgecolor="#FFFFFF", ax=ax)
        ax.axvline(float(stats["line_revenue_median"]) / 1_000, color=ORANGE, linestyle="--", linewidth=2, label=f"Median {inr(stats['line_revenue_median'])}")
        chart_style(
            ax,
            "Transaction-Line Revenue Distribution",
            "Histogram reveals spread, skew and unusually large order lines",
            ylabel="Transaction lines",
            xlabel="Revenue per order line (₹ thousand)",
        )
        ax.legend(frameon=False)
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    with right:
        discount_analysis = data.assign(
            discount_band=pd.cut(
                data["discount_pct"],
                bins=[-0.001, 0.05, 0.10, 0.15, 0.20, 1.0],
                labels=["0–5%", "5–10%", "10–15%", "15–20%", "20%+"],
            )
        )
        discount_analysis = discount_analysis.groupby("discount_band", observed=True, as_index=False).agg(
            revenue=("revenue", "sum"), profit=("profit", "sum"), transaction_lines=("order_id", "size")
        )
        discount_analysis["profit_margin"] = discount_analysis["profit"] / discount_analysis["revenue"].replace(0, np.nan)
        fig, ax = plt.subplots(figsize=(7.8, 4.7))
        bars = ax.bar(
            discount_analysis["discount_band"].astype(str),
            discount_analysis["profit_margin"] * 100,
            color=[BLUE, CYAN, GOLD, ORANGE, PURPLE][: len(discount_analysis)],
            edgecolor="#FFFFFF",
        )
        chart_style(
            ax,
            "Profit Margin by Discount Band",
            "Aggregated profit ÷ revenue within each promotion range",
            ylabel="Profit margin (%)",
            xlabel="Discount band",
        )
        ax.bar_label(bars, fmt="%.1f%%", padding=3, fontsize=8, color=INK)
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    st.caption(
        "Statistical notes: correlation describes association, not causation. The return interval is a normal approximation using distinct orders and should be interpreted as portfolio evidence, not a forecast."
    )

    section_heading(
        "Connected Deliverables",
        "The browser dashboard uses the same governed definitions as the SQL database, Excel workbook and Power BI assets.",
        "🔗",
        "project-deliverables",
    )
    st.success(
        "One project, multiple audiences: analysts can rerun Python and SQL, managers can use Excel or Power BI, and customers can explore the Streamlit dashboard in a browser."
    )


def render_download_hub(filtered: pd.DataFrame) -> None:
    st.markdown(
        """
        <div id="downloads" style="scroll-margin-top:5.2rem"></div><div class="dashboard-hub">
          <h3>🔗 Connected Dashboard &amp; Download Hub</h3>
          <p>Access the interactive data extract, Excel dashboard, SQL database, Power BI measures and quality documentation from one browser page.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    first = st.columns(4)
    first[0].download_button(
        "⬇ Filtered CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="filtered_retail_transactions.csv",
        mime="text/csv",
        width="stretch",
    )
    first[1].download_button(
        "📊 Excel Dashboard",
        data=read_download_bytes(str(EXCEL_PATH)),
        file_name=EXCEL_PATH.name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )
    first[2].download_button(
        "🗄 SQLite Database",
        data=read_download_bytes(str(DATABASE_PATH)),
        file_name=DATABASE_PATH.name,
        mime="application/vnd.sqlite3",
        width="stretch",
    )
    first[3].download_button(
        "📐 Power BI DAX",
        data=read_download_bytes(str(DAX_PATH)),
        file_name=DAX_PATH.name,
        mime="text/plain",
        width="stretch",
    )

    second = st.columns(4)
    second[0].download_button(
        "⚙ Power Query M",
        data=read_download_bytes(str(POWER_QUERY_PATH)),
        file_name=POWER_QUERY_PATH.name,
        mime="text/plain",
        width="stretch",
    )
    second[1].download_button(
        "📝 Quality Report",
        data=read_download_bytes(str(QUALITY_REPORT_PATH)),
        file_name=QUALITY_REPORT_PATH.name,
        mime="text/markdown",
        width="stretch",
    )
    second[2].link_button("🌐 Portfolio", PORTFOLIO_URL, width="stretch")
    second[3].link_button("💻 GitHub", GITHUB_URL, width="stretch")


try:
    transactions = cached_transactions(str(DATABASE_PATH))
except Exception as exc:
    st.error(f"The analytics database could not be loaded: {exc}")
    st.stop()

page, selected_dates, selected_regions, selected_categories, selected_channels, selected_segments = render_sidebar(transactions)

filtered = apply_filters(
    transactions,
    (pd.Timestamp(selected_dates[0]), pd.Timestamp(selected_dates[1])),
    selected_regions,
    selected_categories,
    selected_channels,
    selected_segments,
)
scoped = has_scope_filters(selected_regions, selected_categories, selected_channels, selected_segments)
quality_summary = cached_quality_summary(str(PROJECT_ROOT))

first_day, last_day = transactions["order_date"].min(), transactions["order_date"].max()
render_hero(
    [
        "👤 Built by Aamir Husain Azad",
        f"📅 {first_day:%b %Y} – {last_day:%b %Y}",
        f"🛡️ {quality_summary.get('checks_passed', '—')}/{quality_summary.get('checks_total', '—')} quality checks",
        "🧪 Synthetic portfolio data",
    ]
)
if filtered.empty:
    st.warning("No transactions match these filters. Remove a filter or press **Reset filters** in the sidebar.", icon="🔎")
    st.stop()

render_kpis(filtered)

if page == "📈 Executive Overview":
    render_overview(filtered, scoped)
elif page == "👥 Customer Intelligence":
    render_customer_360(filtered)
elif page == "🛍️ Products & Returns":
    render_products(filtered)
elif page == "🛡️ Data Quality":
    render_quality(filtered)
else:
    render_project_stack(filtered)

render_download_hub(filtered)
render_footer()
render_back_to_top()
