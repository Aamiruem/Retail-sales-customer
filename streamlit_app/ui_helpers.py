"""Shared visual components for the Streamlit retail dashboard."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st


BLUE = "#2563EB"
PURPLE = "#7C3AED"
CYAN = "#0891B2"
GOLD = "#D4A72C"
ORANGE = "#E57A32"
OLIVE = "#7B8B3A"
PINK = "#C65D8A"
NAVY = "#132A53"
INK = "#1F2937"
MUTED = "#64748B"
GRID = "#E5E7EB"
PALETTE = [BLUE, PURPLE, CYAN, GOLD, ORANGE, OLIVE, PINK]


def inject_dashboard_css() -> None:
    st.markdown(
        """
        <style>
          :root { --ink:#1F2937; --muted:#64748B; --blue:#2563EB; --purple:#7C3AED; }
          html, body, [class*="css"] { font-family: Inter, "Segoe UI", Arial, sans-serif; }
          .stApp {
            background:
              radial-gradient(circle at 88% 2%, rgba(124,58,237,.18), transparent 34rem),
              radial-gradient(circle at 8% 42%, rgba(8,145,178,.13), transparent 30rem),
              radial-gradient(circle at 62% 82%, rgba(37,99,235,.10), transparent 32rem),
              linear-gradient(155deg,#F9FBFF 0%,#ECF4FF 48%,#F8F1FF 100%);
            background-attachment:fixed;
          }
          .block-container { max-width:1540px; padding:1.2rem 1.55rem 2.5rem; }
          [data-testid="stSidebar"] {
            background:
              radial-gradient(circle at 10% 8%,rgba(56,189,248,.23),transparent 13rem),
              linear-gradient(180deg,#101A42 0%,#1D3C86 58%,#5B21B6 125%);
            border-right:1px solid rgba(255,255,255,.14); min-width:19rem;
            box-shadow:9px 0 34px rgba(15,23,42,.18);
          }
          [data-testid="stSidebar"] label p,
          [data-testid="stSidebar"] .stCaption p,
          [data-testid="stSidebar"] h1,
          [data-testid="stSidebar"] h2,
          [data-testid="stSidebar"] h3 { color:#E8EEFF !important; }
          [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#D8E2FF; }
          [data-testid="stSidebar"] [data-baseweb="select"] > div,
          [data-testid="stSidebar"] [data-baseweb="input"] > div {
            background:rgba(255,255,255,.98); border-color:rgba(255,255,255,.25); border-radius:11px;
          }
          [data-testid="stSidebar"] {
            scrollbar-width:thin; scrollbar-color:#60A5FA rgba(255,255,255,.06);
          }
          [data-testid="stSidebar"]::-webkit-scrollbar { width:7px; }
          [data-testid="stSidebar"]::-webkit-scrollbar-thumb { background:#60A5FA; border-radius:999px; }
          [data-testid="stSidebar"] details {
            border:1px solid rgba(255,255,255,.15) !important; border-radius:14px !important;
            background:rgba(255,255,255,.07) !important; margin-top:.45rem;
          }
          [data-testid="stSidebar"] details summary { color:#FFFFFF !important; font-weight:800; }
          .sidebar-brand {
            padding:1rem; margin:.2rem 0 1rem; border:1px solid rgba(255,255,255,.16);
            border-radius:16px; background:rgba(255,255,255,.09); box-shadow:0 12px 26px rgba(0,0,0,.14);
          }
          .sidebar-brand .initials {
            display:inline-grid; place-items:center; width:45px; height:45px; border-radius:14px;
            color:white; font-weight:800; background:linear-gradient(135deg,#38BDF8,#7C3AED);
            box-shadow:0 8px 20px rgba(56,189,248,.25); margin-bottom:.65rem;
          }
          .sidebar-brand h3 { margin:0; font-size:1.05rem; }
          .sidebar-brand p { margin:.28rem 0 0; font-size:.78rem; color:#BFD0FF !important; }
          .filter-summary {
            padding:.8rem .9rem; margin:.7rem 0; border-radius:13px; color:#E8EEFF;
            background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.12); font-size:.78rem;
          }
          .hero {
            position:relative; overflow:hidden; color:white; padding:1.5rem 1.65rem; border-radius:22px;
            margin-bottom:.8rem; background:linear-gradient(120deg,#102A56 0%,#2458B8 52%,#7C3AED 100%);
            box-shadow:0 20px 48px rgba(37,99,235,.22);
          }
          .hero::after {
            content:""; position:absolute; width:230px; height:230px; border-radius:50%; right:-45px; top:-95px;
            border:34px solid rgba(255,255,255,.10); box-shadow:0 0 0 30px rgba(255,255,255,.04);
          }
          .hero .eyebrow { letter-spacing:.14em; font-size:.72rem; font-weight:800; color:#CFE3FF; }
          .hero h1 { margin:.38rem 0 .28rem; font-size:2.25rem; line-height:1.12; }
          .hero p { margin:0; max-width:920px; color:#E4EEFF; font-size:.98rem; }
          .hero-meta { display:flex; gap:.55rem; flex-wrap:wrap; margin-top:1rem; }
          .hero-chip {
            padding:.34rem .65rem; border-radius:999px; font-size:.72rem; font-weight:700;
            background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.18);
          }
          div[data-testid="stRadio"] > div[role="radiogroup"] {
            display:flex; gap:.5rem; padding:.48rem; border-radius:16px; background:#FFFFFF;
            border:1px solid #E1E8F4; box-shadow:0 10px 28px rgba(15,23,42,.07); flex-wrap:wrap;
          }
          div[data-testid="stRadio"] label {
            flex:1 1 190px; justify-content:center; padding:.68rem .8rem; border-radius:11px;
            background:#F1F5FB; border:1px solid transparent; transition:.2s ease;
          }
          div[data-testid="stRadio"] label:hover { border-color:#AFC7F5; transform:translateY(-1px); }
          div[data-testid="stRadio"] label:has(input:checked) {
            background:linear-gradient(120deg,#2563EB,#7C3AED); box-shadow:0 8px 18px rgba(37,99,235,.22);
          }
          div[data-testid="stRadio"] label:has(input:checked) p { color:#FFFFFF !important; font-weight:800; }
          [data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] {
            display:flex; flex-direction:column; gap:.42rem; padding:.45rem; border-radius:15px;
            background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.12);
            box-shadow:none;
          }
          [data-testid="stSidebar"] div[data-testid="stRadio"] label {
            flex:0 0 auto; justify-content:flex-start; min-height:2.65rem; padding:.62rem .72rem;
            background:rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.13);
          }
          [data-testid="stSidebar"] div[data-testid="stRadio"] label p { color:#DCE7FF !important; font-size:.84rem; }
          [data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
            background:linear-gradient(120deg,#2563EB,#7C3AED); border-color:rgba(255,255,255,.24);
            box-shadow:0 8px 20px rgba(0,0,0,.20);
          }
          div[data-testid="stMetric"] {
            position:relative; overflow:hidden; min-height:112px; padding:1rem 1rem .85rem;
            background:linear-gradient(145deg,#FFFFFF,#F8FAFF); border:1px solid #DFE6F1;
            border-radius:16px; box-shadow:0 10px 26px rgba(15,23,42,.07); transition:.2s ease;
          }
          div[data-testid="stMetric"]:hover { transform:translateY(-3px); box-shadow:0 15px 34px rgba(37,99,235,.12); }
          div[data-testid="stMetric"]::before {
            content:""; position:absolute; inset:0 auto 0 0; width:5px; background:#2563EB;
          }
          div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stMetric"]::before { background:#7C3AED; }
          div[data-testid="stHorizontalBlock"] > div:nth-child(3) div[data-testid="stMetric"]::before { background:#0891B2; }
          div[data-testid="stHorizontalBlock"] > div:nth-child(4) div[data-testid="stMetric"]::before { background:#D4A72C; }
          div[data-testid="stHorizontalBlock"] > div:nth-child(5) div[data-testid="stMetric"]::before { background:#E57A32; }
          div[data-testid="stHorizontalBlock"] > div:nth-child(6) div[data-testid="stMetric"]::before { background:#7B8B3A; }
          div[data-testid="stHorizontalBlock"] > div:nth-child(7) div[data-testid="stMetric"]::before { background:#C65D8A; }
          div[data-testid="stMetricLabel"] p { color:#64748B; font-weight:700; font-size:.80rem; }
          div[data-testid="stMetricValue"] { color:#172033; font-weight:800; }
          .kpi-grid {
            display:grid; grid-template-columns:repeat(auto-fit,minmax(145px,1fr)); gap:.72rem;
            margin:.65rem 0 1rem;
          }
          .kpi-card {
            position:relative; overflow:hidden; min-height:126px; padding:1rem 1rem .82rem 1.08rem;
            border-radius:17px; background:linear-gradient(145deg,#FFFFFF,#F6F9FF);
            border:1px solid #DCE5F2; box-shadow:0 11px 28px rgba(15,23,42,.075);
            transition:.2s ease;
          }
          .kpi-card:hover { transform:translateY(-3px); box-shadow:0 17px 36px rgba(37,99,235,.14); }
          .kpi-card::before {
            content:""; position:absolute; inset:0 auto 0 0; width:6px; background:var(--accent,#2563EB);
          }
          .kpi-card::after {
            content:""; position:absolute; width:74px; height:74px; border-radius:50%; right:-28px; top:-30px;
            background:var(--accent,#2563EB); opacity:.08;
          }
          .kpi-card .kpi-top { display:flex; justify-content:space-between; align-items:center; gap:.45rem; }
          .kpi-card .kpi-label { color:#64748B; font-size:.74rem; font-weight:800; line-height:1.25; }
          .kpi-card .kpi-icon { font-size:1.05rem; }
          .kpi-card strong { display:block; margin:.42rem 0 .2rem; color:#172033; font-size:1.42rem; line-height:1.1; }
          .kpi-card small { color:#7B8799; font-size:.66rem; line-height:1.3; }
          .section-heading { margin:1.2rem 0 .65rem; }
          .section-heading h2 { margin:0; color:#172033; font-size:1.35rem; }
          .section-heading p { margin:.22rem 0 0; color:#64748B; font-size:.86rem; }
          .scroll-progress {
            position:fixed; left:0; top:0; width:100%; height:4px; z-index:99999;
            transform-origin:0 50%; background:linear-gradient(90deg,#38BDF8,#2563EB,#7C3AED,#C65D8A);
            animation:dashboard-progress linear; animation-timeline:scroll(root);
          }
          @keyframes dashboard-progress { from { transform:scaleX(0); } to { transform:scaleX(1); } }
          .scroll-nav {
            position:sticky; top:.45rem; z-index:990; display:flex; gap:.45rem; flex-wrap:wrap;
            margin:.35rem 0 .85rem; padding:.52rem; border-radius:15px;
            background:rgba(255,255,255,.92); backdrop-filter:blur(12px);
            border:1px solid #DDE6F4; box-shadow:0 10px 28px rgba(15,23,42,.08);
          }
          .scroll-nav a {
            flex:1 1 135px; text-align:center; text-decoration:none; padding:.52rem .62rem;
            border-radius:10px; color:#34507A; font-size:.76rem; font-weight:800; background:#F1F5FB;
            border:1px solid transparent; transition:.18s ease;
          }
          .scroll-nav a:hover { color:#FFFFFF; background:linear-gradient(110deg,#2563EB,#7C3AED); transform:translateY(-1px); }
          .back-to-top {
            position:fixed; right:1.25rem; bottom:1.25rem; z-index:9999; display:grid; place-items:center;
            width:46px; height:46px; border-radius:50%; text-decoration:none; color:#FFFFFF !important;
            font-size:1.05rem; font-weight:900; background:linear-gradient(135deg,#2563EB,#7C3AED);
            box-shadow:0 12px 28px rgba(37,99,235,.32); border:2px solid rgba(255,255,255,.70);
          }
          .insight-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.75rem; margin:.65rem 0 1rem; }
          .insight-card {
            background:#FFFFFF; border:1px solid #E1E8F4; border-radius:15px; padding:.85rem .95rem;
            box-shadow:0 8px 22px rgba(15,23,42,.05); border-top:4px solid var(--accent,#2563EB);
          }
          .insight-card span { display:block; color:#64748B; font-size:.74rem; font-weight:700; }
          .insight-card strong { display:block; color:#172033; font-size:1.02rem; margin-top:.2rem; }
          .insight-card small { color:#7B8799; font-size:.69rem; }
          .dashboard-hub {
            padding:1.1rem 1.25rem; margin:1.4rem 0 .8rem; border-radius:18px;
            background:linear-gradient(115deg,#EAF2FF,#F4ECFF); border:1px solid #D9E4F8;
          }
          .dashboard-hub h3 { color:#172033; margin:0 0 .25rem; }
          .dashboard-hub p { color:#64748B; margin:0; font-size:.84rem; }
          [data-testid="stImage"] {
            overflow:hidden; border-radius:22px; border:1px solid #D8E4F5;
            box-shadow:0 18px 42px rgba(37,99,235,.15); background:#FFFFFF;
          }
          [data-testid="stImage"] img { border-radius:22px; display:block; }
          .category-grid {
            display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:.78rem;
            margin:.7rem 0 1.1rem;
          }
          .category-card {
            position:relative; overflow:hidden; min-height:160px; padding:1rem;
            border-radius:17px; background:linear-gradient(150deg,#FFFFFF,#F7FAFF);
            border:1px solid #DFE7F3; box-shadow:0 10px 26px rgba(15,23,42,.07);
            border-top:5px solid var(--accent,#2563EB); transition:.2s ease;
          }
          .category-card:hover { transform:translateY(-4px); box-shadow:0 17px 36px rgba(37,99,235,.13); }
          .category-card .category-icon {
            display:grid; place-items:center; width:44px; height:44px; border-radius:14px;
            background:color-mix(in srgb,var(--accent,#2563EB) 14%,white); font-size:1.35rem;
          }
          .category-card h3 { margin:.58rem 0 .3rem; color:#172033; font-size:.92rem; }
          .category-card strong { color:var(--accent,#2563EB); font-size:1.08rem; }
          .category-card p { margin:.4rem 0 0; color:#64748B; font-size:.70rem; line-height:1.42; }
          .catalog-note {
            padding:.8rem 1rem; border-radius:14px; color:#354A6B; font-size:.78rem;
            background:linear-gradient(105deg,#E8F2FF,#F1E9FF); border:1px solid #D7E3F5;
          }
          .tech-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.8rem; margin:.7rem 0 1.2rem; }
          .tech-card {
            min-height:142px; padding:1rem; border-radius:16px; background:#FFFFFF; border:1px solid #E1E8F4;
            box-shadow:0 9px 24px rgba(15,23,42,.06); border-top:4px solid var(--accent,#2563EB);
            transition:.2s ease;
          }
          .tech-card:hover { transform:translateY(-4px); box-shadow:0 16px 34px rgba(37,99,235,.12); }
          .tech-card .tech-icon { font-size:1.45rem; }
          .tech-card h3 { margin:.35rem 0 .3rem; color:#172033; font-size:1rem; }
          .tech-card p { margin:0; color:#64748B; font-size:.76rem; line-height:1.45; }
          .tech-card small { display:block; margin-top:.55rem; color:var(--accent,#2563EB); font-weight:800; font-size:.67rem; }
          .pipeline {
            display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:.65rem; margin:.75rem 0 1.25rem;
          }
          .pipeline-step {
            position:relative; min-height:108px; padding:.85rem .75rem; border-radius:15px; text-align:center;
            background:linear-gradient(145deg,#FFFFFF,#F7FAFF); border:1px solid #DCE6F4;
            box-shadow:0 8px 20px rgba(15,23,42,.05);
          }
          .pipeline-step:not(:last-child)::after {
            content:"→"; position:absolute; right:-.56rem; top:37%; color:#7C3AED; font-size:1.15rem; font-weight:900;
          }
          .pipeline-step b { display:block; color:#172033; font-size:.82rem; margin-top:.32rem; }
          .pipeline-step span { color:#64748B; font-size:.67rem; line-height:1.35; }
          .stButton button, .stDownloadButton button, .stLinkButton a {
            border-radius:11px !important; font-weight:750 !important; min-height:2.65rem;
            border:1px solid #C9D8F3 !important; transition:.2s ease;
          }
          .stButton button:hover, .stDownloadButton button:hover, .stLinkButton a:hover {
            transform:translateY(-2px); box-shadow:0 9px 20px rgba(37,99,235,.14);
          }
          [data-testid="stDataFrame"], [data-testid="stTable"] {
            border-radius:14px; overflow:hidden; box-shadow:0 9px 24px rgba(15,23,42,.06);
          }
          .footer {
            margin-top:1.5rem; padding:1.25rem; text-align:center; color:#D9E5FF;
            border-radius:18px; background:linear-gradient(110deg,#0B1739,#173A72);
          }
          .footer strong { color:#FFFFFF; }
          .footer .stack { margin-top:.5rem; color:#9FC2FF; font-size:.75rem; }
          @media (max-width:900px) {
            .block-container { padding:1rem .85rem 2rem; }
            .hero h1 { font-size:1.65rem; }
            .insight-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
            .tech-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
            .pipeline { grid-template-columns:repeat(2,minmax(0,1fr)); }
            .pipeline-step::after { display:none; }
            [data-testid="stSidebar"] { min-width:18rem; }
          }
          @media (max-width:640px) {
            .kpi-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
            .kpi-card { min-height:116px; }
            .category-grid { grid-template-columns:1fr; }
            .scroll-nav a { flex:1 1 44%; }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div id="retail-top"></div><div class="scroll-progress"></div><div class="hero">
          <div class="eyebrow">RETAIL ANALYTICS COMMAND CENTER</div>
          <h1>Retail Sales &amp; Customer Insights</h1>
          <p>Explore sales movement, customer value, product performance, returns, targets and data quality from one connected browser dashboard.</p>
          <div class="hero-meta">
            <span class="hero-chip">👤 Built by Aamir Husain Azad</span>
            <span class="hero-chip">📅 Jan 2024–Dec 2025</span>
            <span class="hero-chip">🛡️ 15/15 quality checks</span>
            <span class="hero-chip">🧪 Synthetic portfolio data</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(title: str, note: str, icon: str, anchor: str | None = None) -> None:
    anchor_markup = f'<div id="{anchor}" style="scroll-margin-top:5.2rem"></div>' if anchor else ""
    st.markdown(
        f'{anchor_markup}<div class="section-heading"><h2>{icon} {title}</h2><p>{note}</p></div>',
        unsafe_allow_html=True,
    )


def scroll_menu(items: list[tuple[str, str]]) -> None:
    links = "".join(f'<a href="#{anchor}">{label}</a>' for anchor, label in items)
    st.markdown(f'<nav class="scroll-nav">{links}</nav>', unsafe_allow_html=True)


def kpi_cards(items: list[tuple[str, str, str, str, str]]) -> None:
    cards = "".join(
        f'<article class="kpi-card" style="--accent:{color}"><div class="kpi-top"><span class="kpi-label">{label}</span><span class="kpi-icon">{icon}</span></div><strong>{value}</strong><small>{note}</small></article>'
        for label, value, note, icon, color in items
    )
    st.markdown(f'<div class="kpi-grid">{cards}</div>', unsafe_allow_html=True)


def category_gallery_cards(items: list[tuple[str, str, str, str, str]]) -> None:
    cards = "".join(
        f'<article class="category-card" style="--accent:{color}"><div class="category-icon">{icon}</div><h3>{title}</h3><strong>{value}</strong><p>{detail}</p></article>'
        for icon, title, value, detail, color in items
    )
    st.markdown(f'<div class="category-grid">{cards}</div>', unsafe_allow_html=True)


def technology_cards(items: list[tuple[str, str, str, str, str]]) -> None:
    cards = "".join(
        f'<article class="tech-card" style="--accent:{color}"><div class="tech-icon">{icon}</div><h3>{title}</h3><p>{description}</p><small>{tools}</small></article>'
        for icon, title, description, tools, color in items
    )
    st.markdown(f'<div class="tech-grid">{cards}</div>', unsafe_allow_html=True)


def pipeline_steps(items: list[tuple[str, str, str]]) -> None:
    steps = "".join(
        f'<div class="pipeline-step"><div style="font-size:1.35rem">{icon}</div><b>{title}</b><span>{description}</span></div>'
        for icon, title, description in items
    )
    st.markdown(f'<div class="pipeline">{steps}</div>', unsafe_allow_html=True)


def render_back_to_top() -> None:
    st.markdown('<a class="back-to-top" href="#retail-top" title="Back to top">↑</a>', unsafe_allow_html=True)


def insight_cards(items: list[tuple[str, str, str, str]]) -> None:
    cards = "".join(
        f'<div class="insight-card" style="--accent:{color}"><span>{label}</span><strong>{value}</strong><small>{note}</small></div>'
        for label, value, note, color in items
    )
    st.markdown(f'<div class="insight-grid">{cards}</div>', unsafe_allow_html=True)


def chart_style(ax: plt.Axes, title: str, subtitle: str, ylabel: str = "", xlabel: str = "") -> None:
    ax.figure.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    ax.set_title(title, loc="left", fontsize=13, color=INK, pad=24, fontweight="bold")
    ax.text(0, 1.015, subtitle, transform=ax.transAxes, fontsize=8.5, color=MUTED, va="bottom")
    ax.set_ylabel(ylabel, color=MUTED, fontsize=9)
    ax.set_xlabel(xlabel, color=MUTED, fontsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.7)
    ax.grid(axis="x", visible=False)
    ax.tick_params(colors=MUTED, labelsize=8.5, length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)


@st.cache_data(show_spinner=False)
def read_download_bytes(path: str) -> bytes:
    return Path(path).read_bytes()


def render_footer() -> None:
    st.markdown(
        """
        <div class="footer">
          <strong>Designed &amp; developed by Aamir Husain Azad</strong><br>
          AI/ML &amp; Data Analytics Portfolio Project · All records are synthetic
          <div class="stack">Python · SQL · SQLite · Pandas · NumPy · Matplotlib · Seaborn · Streamlit · Excel · Power BI · Power Query · DAX</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
