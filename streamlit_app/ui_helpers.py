"""Shared visual components for the Streamlit retail dashboard."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st


BLUE = "#2563EB"
PURPLE = "#6366F1"
CYAN = "#0EA5E9"
GOLD = "#F59E0B"
ORANGE = "#F97316"
OLIVE = "#10B981"
PINK = "#EC4899"
NAVY = "#0B1533"
INK = "#0F172A"
MUTED = "#64748B"
GRID = "#EEF2F7"
PALETTE = [BLUE, PURPLE, CYAN, GOLD, ORANGE, OLIVE, PINK]


def inject_dashboard_css() -> None:
    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
          :root {
            --ink:#0F172A; --body:#334155; --muted:#64748B; --line:#E2E8F0; --surface:#FFFFFF;
            --canvas:#F4F6FB; --blue:#2563EB; --indigo:#4F46E5; --radius:16px;
            --shadow:0 1px 2px rgba(15,23,42,.04), 0 8px 24px rgba(15,23,42,.06);
          }
          html, body, [class*="css"], .stApp, button, input, textarea, select { font-family:Inter,"Segoe UI",Arial,sans-serif; }
          .stApp { background:var(--canvas); }
          header[data-testid="stHeader"] { background:rgba(244,246,251,.85); backdrop-filter:blur(8px); }
          .block-container { max-width:1480px; padding:3.6rem 2rem 2.5rem; }

          /* ---------- Sidebar ---------- */
          [data-testid="stSidebar"] {
            background:linear-gradient(180deg,#0B1533 0%,#13265A 70%,#1E2F73 100%);
            border-right:1px solid rgba(255,255,255,.08);
          }
          [data-testid="stSidebar"] * { color:#E2E8F0; }
          [data-testid="stSidebar"] h3 { font-size:.72rem !important; letter-spacing:.14em; text-transform:uppercase;
            color:#93A4C8 !important; margin:1.1rem 0 .45rem !important; font-weight:700; }
          [data-testid="stSidebar"] label p { color:#CBD5E1 !important; font-size:.8rem; font-weight:600; }
          [data-testid="stSidebar"] [data-baseweb="select"] > div,
          [data-testid="stSidebar"] [data-baseweb="input"] > div {
            background:#FFFFFF; border:none; border-radius:10px;
          }
          [data-testid="stSidebar"] [data-baseweb="select"] *, [data-testid="stSidebar"] [data-baseweb="input"] *,
          [data-testid="stSidebar"] input { color:#0F172A !important; -webkit-text-fill-color:#0F172A !important; opacity:1 !important; }
          [data-testid="stSidebar"] [data-testid="stDateInput"] [data-baseweb] * { color:#0F172A !important; -webkit-text-fill-color:#0F172A !important; }
          [data-testid="stSidebar"] [data-testid="stDateInput"] > div > div { background:#FFFFFF !important; border-radius:10px; }
          [data-testid="stSidebar"] input::placeholder { color:#64748B !important; -webkit-text-fill-color:#64748B !important; }
          [data-testid="stSidebar"] [data-baseweb="tag"] { background:#E0E7FF !important; }
          [data-testid="stSidebar"] details {
            border:1px solid rgba(255,255,255,.12) !important; border-radius:14px !important;
            background:rgba(255,255,255,.05) !important;
          }
          [data-testid="stSidebar"] details summary,
          [data-testid="stSidebar"] details summary:hover { background:transparent !important; }
          [data-testid="stSidebar"] details summary p,
          [data-testid="stSidebar"] details summary span { color:#FFFFFF !important; font-weight:700; }
          [data-testid="stSidebar"] .stButton button {
            width:100%; background:rgba(255,255,255,.10) !important; color:#FFFFFF !important;
            border:1px solid rgba(255,255,255,.22) !important;
          }
          [data-testid="stSidebar"] .stButton button p { color:#FFFFFF !important; }
          [data-testid="stSidebar"] .stButton button:hover { background:rgba(255,255,255,.18) !important; }
          [data-testid="stSidebar"] .stLinkButton a { background:rgba(255,255,255,.08) !important; border:1px solid rgba(255,255,255,.18) !important; }
          [data-testid="stSidebar"] .stLinkButton a p { color:#FFFFFF !important; }
          .sidebar-brand { display:flex; gap:.75rem; align-items:center; padding:.9rem; margin:.1rem 0 .4rem;
            border-radius:14px; background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.10); }
          .sidebar-brand .initials { flex:none; display:grid; place-items:center; width:42px; height:42px; border-radius:12px;
            color:#fff; font-weight:800; background:linear-gradient(135deg,#38BDF8,#6366F1); }
          .sidebar-brand h4 { margin:0; font-size:.95rem; color:#FFFFFF; font-weight:700; }
          .sidebar-brand p { margin:.1rem 0 0; font-size:.74rem; color:#A5B4FC !important; }
          .filter-summary { padding:.7rem .8rem; margin:.6rem 0; border-radius:12px; font-size:.76rem; line-height:1.5;
            background:rgba(99,102,241,.16); border:1px solid rgba(165,180,252,.25); }
          .filter-summary strong { color:#FFFFFF; }
          .sidebar-note { font-size:.72rem; color:#93A4C8 !important; margin-top:.8rem; }

          /* Sidebar page navigation */
          [data-testid="stSidebar"] div[role="radiogroup"] { display:flex; flex-direction:column; gap:.3rem; }
          [data-testid="stSidebar"] div[role="radiogroup"] label {
            width:100%; margin:0; padding:.6rem .75rem; border-radius:10px; border:1px solid transparent;
            background:transparent; transition:background .15s ease;
          }
          [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display:none; }
          [data-testid="stSidebar"] div[role="radiogroup"] label:hover { background:rgba(255,255,255,.07); }
          [data-testid="stSidebar"] div[role="radiogroup"] label p { font-size:.88rem; font-weight:500; color:#CBD5E1 !important; }
          [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
            background:linear-gradient(90deg,rgba(99,102,241,.95),rgba(37,99,235,.95)); box-shadow:0 6px 16px rgba(37,99,235,.35);
          }
          [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p { color:#FFFFFF !important; font-weight:700; }

          /* ---------- Hero ---------- */
          .hero { position:relative; overflow:hidden; color:#fff; padding:1.6rem 1.8rem; border-radius:20px; margin-bottom:1.1rem;
            background:radial-gradient(circle at 92% 0%,rgba(129,140,248,.55),transparent 22rem),
                       linear-gradient(120deg,#0B1533 0%,#1E3A8A 60%,#4338CA 100%);
            box-shadow:0 18px 40px rgba(30,58,138,.22); }
          .hero .eyebrow { letter-spacing:.16em; font-size:.7rem; font-weight:700; color:#A5B4FC; text-transform:uppercase; }
          .hero h1 { margin:.35rem 0 .3rem; font-size:2.05rem; line-height:1.15; font-weight:800; color:#fff; padding:0; }
          .hero p { margin:0; max-width:860px; color:#DBE4FF; font-size:.95rem; line-height:1.55; }
          .hero-meta { display:flex; gap:.5rem; flex-wrap:wrap; margin-top:1rem; }
          .hero-chip { padding:.32rem .7rem; border-radius:999px; font-size:.72rem; font-weight:600;
            background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.18); }

          /* ---------- KPI cards ---------- */
          .kpi-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(138px,1fr)); gap:.75rem; margin:0 0 1.2rem; }
          .kpi-card { position:relative; padding:1rem 1.05rem .9rem; border-radius:var(--radius); background:var(--surface);
            border:1px solid var(--line); box-shadow:var(--shadow); transition:transform .15s ease, box-shadow .15s ease; }
          .kpi-card:hover { transform:translateY(-2px); box-shadow:0 12px 28px rgba(15,23,42,.10); }
          .kpi-card .kpi-top { display:flex; justify-content:space-between; align-items:center; }
          .kpi-card .kpi-label { color:var(--muted); font-size:.74rem; font-weight:600; text-transform:uppercase; letter-spacing:.05em; }
          .kpi-card .kpi-icon { display:grid; place-items:center; width:30px; height:30px; border-radius:9px; font-size:.95rem;
            background:color-mix(in srgb,var(--accent,#2563EB) 12%,white); }
          .kpi-card strong { display:block; margin:.5rem 0 .2rem; color:var(--ink); font-size:clamp(1.15rem,1.6vw,1.5rem); font-weight:800;
            letter-spacing:-.01em; font-variant-numeric:tabular-nums; }
          .kpi-card small { color:var(--muted); font-size:.72rem; }
          .kpi-card::after { content:""; position:absolute; left:1.05rem; right:1.05rem; bottom:0; height:3px;
            border-radius:3px 3px 0 0; background:var(--accent,#2563EB); opacity:.85; }

          /* ---------- Sections ---------- */
          .section-heading { margin:1.6rem 0 .75rem; }
          .section-heading h2 { margin:0; padding:0; color:var(--ink); font-size:1.2rem; font-weight:700; }
          .section-heading p { margin:.2rem 0 0; color:var(--muted); font-size:.86rem; }
          .scroll-progress { position:fixed; left:0; top:0; width:100%; height:3px; z-index:999999; transform-origin:0 50%;
            background:linear-gradient(90deg,#38BDF8,#2563EB,#6366F1); animation:dashboard-progress linear; animation-timeline:scroll(root); }
          @keyframes dashboard-progress { from { transform:scaleX(0); } to { transform:scaleX(1); } }
          .scroll-nav { position:sticky; top:3.4rem; z-index:990; display:flex; gap:.35rem; flex-wrap:wrap; margin:0 0 .4rem; padding:.35rem;
            border-radius:12px; background:rgba(255,255,255,.92); backdrop-filter:blur(10px); border:1px solid var(--line); box-shadow:var(--shadow); }
          .scroll-nav a { flex:1 1 120px; text-align:center; text-decoration:none; padding:.45rem .6rem; border-radius:8px;
            color:#334155 !important; font-size:.78rem; font-weight:600; transition:.15s ease; }
          .scroll-nav a:hover { color:#fff !important; background:var(--blue); }
          .back-to-top { position:fixed; right:1.2rem; bottom:1.2rem; z-index:9999; display:grid; place-items:center; width:42px; height:42px;
            border-radius:50%; text-decoration:none; color:#fff !important; font-weight:800; background:var(--indigo);
            box-shadow:0 10px 24px rgba(79,70,229,.35); }

          .insight-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.8rem; margin:.2rem 0 .6rem; }
          .insight-card { background:var(--surface); border:1px solid var(--line); border-radius:14px; padding:.9rem 1rem;
            box-shadow:var(--shadow); border-left:4px solid var(--accent,#2563EB); }
          .insight-card span { display:block; color:var(--muted); font-size:.72rem; font-weight:600; text-transform:uppercase; letter-spacing:.05em; }
          .insight-card strong { display:block; color:var(--ink); font-size:1.08rem; font-weight:700; margin:.25rem 0 .1rem;
            white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
          .insight-card small { color:var(--muted); font-size:.74rem; }

          /* Charts, tables, images, callouts */
          [data-testid="stImage"] img, [data-testid="stPyplot"] img { border-radius:14px; }
          [data-testid="stPyplot"], [data-testid="stImage"] { background:var(--surface); border:1px solid var(--line);
            border-radius:var(--radius); box-shadow:var(--shadow); padding:.35rem; }
          [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:14px; overflow:hidden; box-shadow:var(--shadow); background:#fff; }
          [data-testid="stAlert"] { border-radius:12px; }
          div[data-testid="stMetric"] { padding:1rem; background:var(--surface); border:1px solid var(--line); border-radius:var(--radius); box-shadow:var(--shadow); }
          div[data-testid="stMetricLabel"] p { color:var(--muted); font-weight:600; font-size:.78rem; text-transform:uppercase; letter-spacing:.05em; }
          div[data-testid="stMetricValue"] { color:var(--ink); font-weight:800; }
          .note { padding:.75rem 1rem; border-radius:12px; font-size:.82rem; color:#1E3A8A; background:#EEF2FF; border:1px solid #C7D2FE; margin:.4rem 0 .8rem; }
          .note.warn { color:#7C2D12; background:#FFF7ED; border-color:#FED7AA; }

          .category-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:.8rem; margin:.4rem 0 1rem; }
          .category-card { padding:1rem; border-radius:var(--radius); background:var(--surface); border:1px solid var(--line);
            box-shadow:var(--shadow); border-top:4px solid var(--accent,#2563EB); transition:.15s ease; }
          .category-card:hover { transform:translateY(-2px); }
          .category-card .category-icon { display:grid; place-items:center; width:40px; height:40px; border-radius:12px;
            background:color-mix(in srgb,var(--accent,#2563EB) 12%,white); font-size:1.2rem; }
          .category-card h3 { margin:.6rem 0 .25rem; padding:0; color:var(--ink); font-size:.95rem; font-weight:700; }
          .category-card strong { color:var(--accent,#2563EB); font-size:1.15rem; font-weight:800; }
          .category-card p { margin:.4rem 0 0; color:var(--muted); font-size:.74rem; line-height:1.5; }
          .catalog-note { padding:.7rem 1rem; border-radius:12px; color:#334155; font-size:.8rem; background:#F1F5F9; border:1px solid var(--line); margin-bottom:.5rem; }

          .tech-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.8rem; margin:.4rem 0 1rem; }
          .tech-card { padding:1rem; border-radius:var(--radius); background:var(--surface); border:1px solid var(--line); box-shadow:var(--shadow); }
          .tech-card .tech-icon { font-size:1.35rem; }
          .tech-card h3 { margin:.35rem 0 .3rem; padding:0; color:var(--ink); font-size:.98rem; font-weight:700; }
          .tech-card p { margin:0; color:var(--muted); font-size:.78rem; line-height:1.5; }
          .tech-card small { display:block; margin-top:.55rem; color:var(--accent,#2563EB); font-weight:700; font-size:.7rem; }
          .pipeline { display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:.7rem; margin:.4rem 0 1rem; }
          .pipeline-step { position:relative; padding:.9rem .75rem; border-radius:14px; text-align:center; background:var(--surface);
            border:1px solid var(--line); box-shadow:var(--shadow); }
          .pipeline-step:not(:last-child)::after { content:"›"; position:absolute; right:-.62rem; top:38%; color:var(--indigo); font-size:1.3rem; font-weight:800; }
          .pipeline-step b { display:block; color:var(--ink); font-size:.84rem; margin-top:.3rem; }
          .pipeline-step span { color:var(--muted); font-size:.7rem; line-height:1.4; }

          .dashboard-hub { padding:1.1rem 1.25rem; margin:2rem 0 .8rem; border-radius:var(--radius); background:var(--surface);
            border:1px solid var(--line); box-shadow:var(--shadow); }
          .dashboard-hub h3 { color:var(--ink); margin:0 0 .2rem; padding:0; font-size:1.05rem; font-weight:700; }
          .dashboard-hub p { color:var(--muted); margin:0; font-size:.82rem; }
          .stButton button, .stDownloadButton button, .stLinkButton a { border-radius:10px !important; font-weight:600 !important;
            min-height:2.6rem; border:1px solid var(--line) !important; background:#fff; transition:.15s ease; }
          .stDownloadButton button:hover, .stLinkButton a:hover { border-color:#93C5FD !important; color:var(--blue) !important; }
          .footer { margin-top:1.6rem; padding:1.2rem; text-align:center; color:#CBD5E1; border-radius:var(--radius); background:#0B1533; font-size:.85rem; }
          .footer strong { color:#fff; }
          .footer .stack { margin-top:.4rem; color:#93A4C8; font-size:.74rem; }

          @media (max-width:1100px) { .insight-grid, .tech-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } .pipeline { grid-template-columns:repeat(3,minmax(0,1fr)); } .pipeline-step::after { display:none; } }
          @media (max-width:640px) {
            .block-container { padding:3.4rem .8rem 2rem; }
            .hero { padding:1.2rem; } .hero h1 { font-size:1.5rem; }
            .kpi-grid { grid-template-columns:repeat(2,minmax(0,1fr)); gap:.6rem; } .kpi-card strong { font-size:1.2rem; }
            .insight-grid, .tech-grid, .pipeline { grid-template-columns:1fr; }
            .scroll-nav { position:static; } .scroll-nav a { flex:1 1 44%; }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(chips: list[str]) -> None:
    chip_markup = "".join(f'<span class="hero-chip">{chip}</span>' for chip in chips)
    st.markdown(
        f"""
        <div id="retail-top"></div><div class="scroll-progress"></div><div class="hero">
          <div class="eyebrow">Retail analytics command center</div>
          <h1>Retail Sales &amp; Customer Insights</h1>
          <p>Sales trends, customer value, product performance, returns, targets and data quality in one interactive dashboard.</p>
          <div class="hero-meta">{chip_markup}</div>
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


plt.rcParams.update(
    {
        "figure.dpi": 150,
        "savefig.dpi": 150,
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "DejaVu Sans", "Arial"],
        "axes.titlesize": 12,
        "legend.fontsize": 8,
        "legend.title_fontsize": 8,
    }
)


def chart_style(ax: plt.Axes, title: str, subtitle: str, ylabel: str = "", xlabel: str = "") -> None:
    ax.figure.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    ax.set_title(title, loc="left", fontsize=12, color=INK, pad=22, fontweight="bold")
    ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=8.5, color=MUTED, va="bottom")
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
          <div class="stack">Python · SQL · SQLite · Pandas · NumPy · scikit-learn · Matplotlib · Seaborn · Streamlit · Excel · Power BI · DAX</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
