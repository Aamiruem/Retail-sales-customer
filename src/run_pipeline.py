"""Run the complete Python pipeline after raw Excel generation."""

from __future__ import annotations

import json

import pandas as pd

from src.analysis import dashboard_tables, kpi_summary
from src.build_star_schema import build_star_schema
from src.config import EXCEL_PAYLOAD, QUALITY_SUMMARY, ensure_directories
from src.etl_pipeline import run_etl
from src.visualizations import build_charts


def _json_records(frame: pd.DataFrame) -> list[dict]:
    ready = frame.copy()
    for column in ready.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns:
        ready[column] = ready[column].dt.strftime("%Y-%m-%d")
    ready = ready.astype(object).where(pd.notnull(ready), None)
    return ready.to_dict(orient="records")


def run() -> None:
    ensure_directories()
    clean, quality_checks = run_etl()
    schema = build_star_schema(clean)
    tables = dashboard_tables(clean, schema["monthly_targets"], schema["customer_rfm"])
    build_charts(clean, schema["monthly_targets"], schema["customer_rfm"])

    payload = {
        "metadata": {
            "title": "Retail Sales & Customer Insights Analytics Dashboard",
            "dataset_type": "Synthetic",
            "date_range": f"{clean['order_date'].min():%Y-%m-%d} to {clean['order_date'].max():%Y-%m-%d}",
            "quality_status": json.loads(QUALITY_SUMMARY.read_text(encoding="utf-8"))["overall_status"],
        },
        "kpis": kpi_summary(clean),
        "transactions": _json_records(clean),
        "monthly": _json_records(tables["monthly"]),
        "category": _json_records(tables["category"]),
        "region": _json_records(tables["region"]),
        "channel": _json_records(tables["channel"]),
        "rfm": _json_records(schema["customer_rfm"]),
        "rfm_summary": _json_records(tables["rfm_summary"]),
        "discount": _json_records(tables["discount"]),
        "top_products": _json_records(tables["top_products"]),
        "quality_checks": _json_records(quality_checks),
    }
    EXCEL_PAYLOAD.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Dashboard payload written to {EXCEL_PAYLOAD}")


if __name__ == "__main__":
    run()
