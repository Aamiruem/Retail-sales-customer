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
    load_quality_checks,
    load_transactions,
    monthly_performance,
    statistical_snapshot,
    top_products,
)
from streamlit_app.ui_helpers import (  # noqa: E402
    BLUE,
    CYAN,
    GOLD,
    INK,
    MUTED,
    OLIVE,
    ORANGE,
    PALETTE,
    PINK,
    PURPLE,
    chart_style,
    inject_dashboard_css,
    insight_cards,
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
    initial_sidebar_state="expanded",
)

DATABASE_PATH = PROJECT_ROOT / "data" / "database" / "retail_analytics.db"
EXCEL_PATH = PROJECT_ROOT / "excel" / "Retail_Sales_Customer_Insights_Dashboard.xlsx"
DAX_PATH = PROJECT_ROOT / "power_bi" / "dax" / "Measures.dax"
POWER_QUERY_PATH = PROJECT_ROOT / "power_bi" / "power_query" / "Load_Star_Schema.m"
QUALITY_REPORT_PATH = PROJECT_ROOT / "reports" / "data_quality_report.md"
PORTFOLIO_URL = "https://aamir-ai-ml-portfolio.aamirhussainazad786.chatgpt.site/"
GITHUB_URL = "https://github.com/Aamiruem"

inject_dashboard_css()


@st.cache_data(show_spinner=False)
def cached_transactions(path: str) -> pd.DataFrame:
    return load_transactions(path)


@st.cache_data(show_spinner=False)
def cached_quality(project_root: str) -> pd.DataFrame:
    return load_quality_checks(project_root)


def format_inr_millions(value: float) -> str:
    return f"₹{value / 1_000_000:,.1f}M"


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
              <h3>Aamir Husain Azad</h3>
              <p>AI/ML &amp; Data Analytics Portfolio</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("### 🧭 Dashboard Navigation")
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

        with st.expander("🎛️ Customer & Sales Filters", expanded=True):
            selected_dates = st.date_input(
                "Order date",
                min_value=minimum_date,
                max_value=maximum_date,
                key="filter_dates",
            )
            if not isinstance(selected_dates, (tuple, list)) or len(selected_dates) != 2:
                selected_dates = (minimum_date, maximum_date)

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
                  {active_filter_count} optional filter group(s) selected
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.button(
                "↻ Reset all filters",
                width="stretch",
                on_click=reset_filters,
                args=(minimum_date, maximum_date),
            )

        with st.expander("🔗 Portfolio & GitHub"):
            st.link_button("🌐 Open Portfolio", PORTFOLIO_URL, width="stretch")
            st.link_button("💻 Open GitHub Profile", GITHUB_URL, width="stretch")
        st.caption("4,180 validated lines · INR · Synthetic data")

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
    columns = st.columns(7)
    columns[0].metric("Revenue", format_inr_millions(kpis["revenue"]))
    columns[1].metric("Profit", format_inr_millions(kpis["profit"]))
    columns[2].metric("Profit Margin", f"{kpis['profit_margin']:.1%}")
    columns[3].metric("Orders", f"{kpis['orders']:,}")
    columns[4].metric("Customers", f"{kpis['customers']:,}")
    columns[5].metric("Return Rate", f"{kpis['return_rate']:.1%}")
    columns[6].metric("Avg Order Value", f"₹{kpis['average_order_value']:,.0f}")
    return kpis


def render_overview(data: pd.DataFrame) -> None:
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
        "Monitor performance, movement, target delivery and the strongest revenue drivers.",
        "📈",
        "overview-summary",
    )
    insight_cards(
        [
            ("Top category", str(best_category["category"]), format_inr_millions(float(best_category["revenue"])), BLUE),
            ("Top region", best_region, "Highest filtered revenue", PURPLE),
            ("Best month", str(best_month["year_month"]), format_inr_millions(float(best_month["revenue"])), CYAN),
            ("Target attainment", f"{target_attainment:.1%}", "Actual revenue ÷ target", GOLD),
        ]
    )

    section_heading("Performance Trends", "Track monthly movement and category contribution.", "📊", "overview-trends")
    left, right = st.columns([1.3, 1])
    with left:
        fig, ax = plt.subplots(figsize=(9.3, 4.3))
        ax.plot(monthly["year_month"], monthly["revenue"] / 1_000_000, color=BLUE, linewidth=2.6, marker="o", label="Revenue")
        ax.plot(monthly["year_month"], monthly["profit"] / 1_000_000, color=GOLD, linewidth=2.3, marker="s", label="Profit")
        chart_style(ax, "Monthly Revenue and Profit", "INR million · filtered monthly movement", ylabel="₹ million")
        ax.tick_params(axis="x", rotation=55, labelsize=8)
        ax.legend(frameon=False, ncol=2, loc="upper left")
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    with right:
        ordered = category.sort_values("revenue")
        colors = [PALETTE[index % len(PALETTE)] for index in range(len(ordered))]
        fig, ax = plt.subplots(figsize=(7.3, 4.3))
        bars = ax.barh(ordered["category"], ordered["revenue"] / 1_000_000, color=colors, edgecolor="#FFFFFF")
        chart_style(ax, "Revenue by Product Category", "INR million · categories ranked by revenue", xlabel="₹ million")
        ax.bar_label(bars, fmt="%.1f", padding=4, fontsize=8, color=INK)
        ax.set_xlim(0, ordered["revenue"].max() / 1_000_000 * 1.15)
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)

    section_heading(
        "Targets & Geographic Mix",
        "Compare plan delivery and identify the regional/category combinations driving revenue.",
        "🎯",
        "overview-targets",
    )
    left, right = st.columns([1.3, 1])
    with left:
        fig, ax = plt.subplots(figsize=(9.3, 4.2))
        x = np.arange(len(monthly))
        ax.bar(x, monthly["target_revenue"] / 1_000_000, color="#DCE6F8", edgecolor="#91AFE4", label="Target")
        ax.plot(x, monthly["revenue"] / 1_000_000, color=PURPLE, marker="o", linewidth=2.3, label="Actual")
        ax.set_xticks(x, monthly["year_month"], rotation=55, fontsize=8)
        chart_style(ax, "Monthly Revenue versus Target", "INR million · actual performance compared with plan", ylabel="₹ million")
        ax.legend(frameon=False, ncol=2, loc="upper left")
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    with right:
        heat = data.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum", fill_value=0) / 1_000_000
        fig, ax = plt.subplots(figsize=(7.3, 4.2))
        cmap = sns.blend_palette(["#EEF5FF", BLUE, PURPLE], as_cmap=True)
        sns.heatmap(heat, annot=True, fmt=".1f", cmap=cmap, linewidths=0.7, cbar_kws={"label": "₹M"}, ax=ax)
        chart_style(ax, "Revenue by Region and Category", "INR million · geographic and category mix")
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(axis="x", rotation=35, labelsize=8)
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
            ("Revenue per customer", f"₹{profile['revenue'].mean():,.0f}", "Average customer value", PINK),
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
        colors = [PALETTE[index % len(PALETTE)] for index in range(len(ordered))]
        fig, ax = plt.subplots(figsize=(7.2, 5.0))
        bars = ax.barh(ordered["rfm_segment"], ordered["customers"], color=colors, edgecolor="#FFFFFF")
        chart_style(ax, "Customers by RFM Segment", "Unique customers · lifecycle segmentation", xlabel="Customers")
        ax.bar_label(bars, padding=4, fontsize=8, color=INK)
        ax.set_xlim(0, ordered["customers"].max() * 1.15)
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    with right:
        segment_names = sorted(profile["rfm_segment"].unique())
        palette_map = {name: PALETTE[index % len(PALETTE)] for index, name in enumerate(segment_names)}
        fig, ax = plt.subplots(figsize=(8.7, 5.0))
        sns.scatterplot(
            data=profile,
            x="recency_days",
            y="orders",
            hue="rfm_segment",
            palette=palette_map,
            alpha=0.72,
            s=46,
            edgecolor="#FFFFFF",
            linewidth=0.4,
            ax=ax,
        )
        chart_style(ax, "Customer Recency and Order Frequency", "One point per customer · lower recency means more recent activity", ylabel="Distinct orders", xlabel="Recency (days)")
        ax.legend(frameon=False, fontsize=7, title="RFM segment", ncol=2)
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
        ax.legend(frameon=False, fontsize=7, title="Cluster / order size", ncol=2)
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    with right:
        ordered_ml = ml_summary.sort_values("average_revenue")
        bar_colors = [cluster_colors.get(name, PURPLE) for name in ordered_ml["ml_cluster"]]
        fig, ax = plt.subplots(figsize=(7.2, 4.9))
        bars = ax.barh(ordered_ml["ml_cluster"], ordered_ml["average_revenue"] / 1_000, color=bar_colors)
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

    cluster_table = ml_summary.copy()
    cluster_table["average_recency_days"] = cluster_table["average_recency_days"].map(lambda value: f"{value:,.0f}")
    cluster_table["average_orders"] = cluster_table["average_orders"].map(lambda value: f"{value:,.1f}")
    cluster_table["average_revenue"] = cluster_table["average_revenue"].map(lambda value: f"₹{value:,.0f}")
    cluster_table["total_revenue"] = cluster_table["total_revenue"].map(format_inr_millions)
    cluster_table["total_profit"] = cluster_table["total_profit"].map(format_inr_millions)
    cluster_table["profit_margin"] = cluster_table["profit_margin"].map(lambda value: f"{value:.1%}")
    st.table(
        cluster_table[
            [
                "ml_cluster",
                "customers",
                "average_recency_days",
                "average_orders",
                "average_revenue",
                "total_revenue",
                "profit_margin",
            ]
        ].rename(
            columns={
                "ml_cluster": "Customer Cluster",
                "customers": "Customers",
                "average_recency_days": "Avg Recency (Days)",
                "average_orders": "Avg Orders",
                "average_revenue": "Avg Revenue",
                "total_revenue": "Total Revenue",
                "profit_margin": "Profit Margin",
            }
        )
    )
    st.info(
        "Action guide: reward High Value customers, cross-sell Loyal Growth, nurture Developing customers, and run win-back campaigns for Needs Attention. ML labels are exploratory—not causal predictions."
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
        ax.barh(y - 0.18, ordered["revenue"] / 1_000_000, height=0.34, color=BLUE, label="Revenue")
        ax.barh(y + 0.18, ordered["profit"] / 1_000_000, height=0.34, color=GOLD, label="Profit")
        ax.set_yticks(y, ordered["customer_segment"])
        chart_style(ax, "Value by Customer Segment", "INR million · revenue and profit comparison", xlabel="₹ million")
        ax.legend(frameon=False, ncol=2, loc="lower right")
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    with right:
        top_customers = profile.head(15).copy()
        top_customers.insert(0, "rank", range(1, len(top_customers) + 1))
        top_customers["revenue"] = top_customers["revenue"].map(lambda value: f"₹{value:,.0f}")
        top_customers["profit"] = top_customers["profit"].map(lambda value: f"₹{value:,.0f}")
        top_customers["last_order"] = top_customers["last_order"].dt.strftime("%d %b %Y")
        st.subheader("🏆 Top Customers by Revenue")
        st.caption("Exact-value lookup for the 15 highest-value customers in the active scope.")
        st.table(
            top_customers[
                ["rank", "customer_name", "rfm_segment", "ml_cluster", "revenue", "profit", "orders", "last_order"]
            ].rename(columns=str.title)
        )


def render_products(data: pd.DataFrame) -> None:
    category = category_performance(data)
    products = top_products(data, limit=12)
    top_product = products.iloc[0]
    high_return_category = category.loc[category["return_rate"].idxmax()]

    scroll_menu(
        [
            ("product-summary", "Summary"),
            ("product-risk", "Return & Discount Risk"),
            ("product-leaders", "Leaderboard"),
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
            ("Top product", str(top_product["product_name"]), format_inr_millions(float(top_product["revenue"])), BLUE),
            ("Top-product margin", f"{top_product['profit_margin']:.1%}", "Profit ÷ revenue", OLIVE),
            ("Highest return category", str(high_return_category["category"]), f"{high_return_category['return_rate']:.1%}", ORANGE),
            ("Units sold", f"{int(data['quantity'].sum()):,}", "Filtered line quantity", PURPLE),
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
        colors = ["#FDBA74", "#FB923C", ORANGE, "#C65D8A", PURPLE][: len(returns)]
        fig, ax = plt.subplots(figsize=(7.6, 4.7))
        bars = ax.barh(returns["category"], returns["return_rate"] * 100, color=colors, edgecolor="#FFFFFF")
        chart_style(ax, "Order Return Rate by Category", "Returned distinct orders ÷ distinct orders", xlabel="% of orders")
        ax.bar_label(bars, labels=[f"{value:.1%}" for value in returns["return_rate"]], padding=4, fontsize=8, color=INK)
        ax.set_xlim(0, returns["return_rate"].max() * 100 * 1.18)
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    with right:
        sample = data.sample(min(1_200, len(data)), random_state=20260804)
        category_names = sorted(sample["category"].unique())
        palette_map = {name: PALETTE[index % len(PALETTE)] for index, name in enumerate(category_names)}
        fig, ax = plt.subplots(figsize=(7.6, 4.7))
        sns.scatterplot(data=sample, x="discount_pct", y="profit", hue="category", palette=palette_map, alpha=0.66, s=34, ax=ax)
        ax.axhline(0, color=INK, linestyle="--", linewidth=0.9)
        chart_style(ax, "Discount and Line Profit", "Up to 1,200 order lines · dashed line marks zero profit", ylabel="Profit (₹)", xlabel="Discount")
        ax.xaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
        ax.legend(frameon=False, fontsize=7, title="Category", ncol=2)
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)

    section_heading(
        "Product Leaderboard",
        "Revenue-ranked products with exact profit, margin, unit and return values.",
        "🏅",
        "product-leaders",
    )
    product_table = products.copy()
    product_table.insert(0, "rank", range(1, len(product_table) + 1))
    product_table["revenue"] = product_table["revenue"].map(lambda value: f"₹{value:,.0f}")
    product_table["profit"] = product_table["profit"].map(lambda value: f"₹{value:,.0f}")
    product_table["profit_margin"] = product_table["profit_margin"].map(lambda value: f"{value:.1%}")
    st.table(product_table.rename(columns=str.title))


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
    q1, q2, q3, q4, q5 = st.columns(5)
    q1.metric("Raw Rows", "4,224")
    q2.metric("Validated Rows", "4,180")
    q3.metric("Rejected Rows", "44")
    q4.metric("Checks Passed", f"{int(checks['passed'].sum())}/{len(checks)}")
    q5.metric("Broken Joins", "0")
    section_heading(
        "Automated Quality Checks",
        "Volume, completeness, uniqueness, ranges, referential integrity and financial arithmetic.",
        "✅",
        "quality-checks",
    )
    displayed = checks[["check_id", "check_name", "actual", "expected", "severity", "status"]].copy()
    st.table(displayed.rename(columns=str.title))
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
            ("Average discount", f"{float(stats['average_discount']):.1%}", "Mean promotional depth", BLUE),
            ("Median line revenue", f"₹{float(stats['line_revenue_median']):,.0f}", "Robust transaction-line midpoint", PURPLE),
            (
                "Return-rate interval",
                f"{float(stats['return_rate_ci_low']):.1%}–{float(stats['return_rate_ci_high']):.1%}",
                "Approximate 95% confidence interval",
                OLIVE,
            ),
        ]
    )

    left, right = st.columns(2)
    with left:
        fig, ax = plt.subplots(figsize=(7.8, 4.7))
        sns.histplot(data["revenue"], bins=28, color=BLUE, alpha=0.82, edgecolor="#FFFFFF", ax=ax)
        ax.axvline(float(stats["line_revenue_median"]), color=ORANGE, linestyle="--", linewidth=2, label="Median")
        chart_style(
            ax,
            "Transaction-Line Revenue Distribution",
            "Histogram reveals spread, skew and unusually large order lines",
            ylabel="Transaction lines",
            xlabel="Revenue (₹)",
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

render_hero()
if filtered.empty:
    st.warning("No transactions match the selected filters. Use the sidebar reset button or remove one or more filters.")
    st.stop()

render_kpis(filtered)

if page == "📈 Executive Overview":
    render_overview(filtered)
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
