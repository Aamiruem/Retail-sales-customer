"""Data-quality rules and rejection tracking for the retail pipeline."""

from __future__ import annotations

import json
from dataclasses import dataclass

import pandas as pd

from src.config import (
    EXPECTED_CLEAN_ROWS,
    EXPECTED_ORDERS,
    EXPECTED_PROFIT,
    EXPECTED_RAW_ROWS,
    EXPECTED_RETURNED_ORDERS,
    EXPECTED_REVENUE,
    QUALITY_CHECKS,
    QUALITY_SUMMARY,
    REJECTED_RECORDS,
)


@dataclass
class QualityResult:
    clean: pd.DataFrame
    rejected: pd.DataFrame
    rejection_counts: dict[str, int]


def clean_and_reject(raw: pd.DataFrame, valid_product_ids: set[str]) -> QualityResult:
    """Apply mutually exclusive validation rules and retain rejection evidence."""
    working = raw.copy()
    rejected_parts: list[pd.DataFrame] = []
    rejection_counts: dict[str, int] = {}

    def reject(mask: pd.Series, reason: str) -> None:
        nonlocal working
        failures = working.loc[mask].copy()
        failures["rejection_reason"] = reason
        rejected_parts.append(failures)
        rejection_counts[reason] = int(len(failures))
        working = working.loc[~mask].copy()

    reject(working.duplicated(subset=["line_id"], keep="first"), "duplicate_line_id")
    reject(working["customer_id"].isna() | working["customer_id"].astype(str).str.strip().eq(""), "missing_customer_id")

    parsed_order_date = pd.to_datetime(working["order_date"], errors="coerce")
    parsed_ship_date = pd.to_datetime(working["ship_date"], errors="coerce")
    reject(parsed_order_date.isna() | parsed_ship_date.isna(), "invalid_date")

    quantity = pd.to_numeric(working["quantity"], errors="coerce")
    reject(quantity.isna() | quantity.le(0), "non_positive_quantity")

    discount = pd.to_numeric(working["discount_pct"], errors="coerce")
    reject(discount.isna() | discount.lt(0) | discount.gt(0.60), "invalid_discount")

    reject(~working["product_id"].isin(valid_product_ids), "invalid_product_id")

    working["order_date"] = pd.to_datetime(working["order_date"], errors="raise")
    working["ship_date"] = pd.to_datetime(working["ship_date"], errors="raise")
    working["quantity"] = pd.to_numeric(working["quantity"], errors="raise").astype(int)
    numeric_columns = [
        "unit_price",
        "discount_pct",
        "gross_sales",
        "discount_amount",
        "sales_after_discount",
        "return_amount",
        "revenue",
        "unit_cost",
        "cost_amount",
        "profit",
        "rating",
    ]
    for column in numeric_columns:
        working[column] = pd.to_numeric(working[column], errors="coerce")

    for column in [
        "customer_id",
        "customer_name",
        "customer_segment",
        "region",
        "state",
        "city",
        "channel",
        "product_name",
        "category",
        "subcategory",
        "payment_method",
    ]:
        working[column] = working[column].astype(str).str.strip()

    # Rating is optional feedback data. Missing ratings are imputed with the
    # observed median and tracked through a dedicated flag.
    working["rating_was_imputed"] = working["rating"].isna().astype(int)
    working["rating"] = working["rating"].fillna(working["rating"].median()).round(1)
    working["return_flag"] = pd.to_numeric(working["return_flag"], errors="raise").astype(int)

    rejected = pd.concat(rejected_parts, ignore_index=True) if rejected_parts else pd.DataFrame()
    return QualityResult(clean=working.reset_index(drop=True), rejected=rejected, rejection_counts=rejection_counts)


def build_quality_report(raw: pd.DataFrame, clean: pd.DataFrame, rejected: pd.DataFrame, rejection_counts: dict[str, int], valid_product_ids: set[str]) -> pd.DataFrame:
    returned_orders = clean.loc[clean["return_flag"].eq(1), "order_id"].nunique()
    checks = [
        ("DQ-001", "Raw volume", len(raw), EXPECTED_RAW_ROWS, len(raw) == EXPECTED_RAW_ROWS, "High"),
        ("DQ-002", "Validated line volume", len(clean), EXPECTED_CLEAN_ROWS, len(clean) == EXPECTED_CLEAN_ROWS, "Critical"),
        ("DQ-003", "Unique line_id", clean["line_id"].nunique(), len(clean), clean["line_id"].is_unique, "Critical"),
        ("DQ-004", "Required IDs complete", int(clean[["line_id", "order_id", "customer_id", "product_id"]].isna().sum().sum()), 0, not clean[["line_id", "order_id", "customer_id", "product_id"]].isna().any().any(), "Critical"),
        ("DQ-005", "Valid date sequence", int((clean["ship_date"] >= clean["order_date"]).sum()), len(clean), bool((clean["ship_date"] >= clean["order_date"]).all()), "High"),
        ("DQ-006", "Positive quantity", int((clean["quantity"] > 0).sum()), len(clean), bool((clean["quantity"] > 0).all()), "High"),
        ("DQ-007", "Discount within 0%-60%", int(clean["discount_pct"].between(0, 0.60).sum()), len(clean), bool(clean["discount_pct"].between(0, 0.60).all()), "High"),
        ("DQ-008", "Product referential integrity", int(clean["product_id"].isin(valid_product_ids).sum()), len(clean), bool(clean["product_id"].isin(valid_product_ids).all()), "Critical"),
        ("DQ-009", "Revenue reconciliation", round(clean["revenue"].sum(), 2), EXPECTED_REVENUE, round(clean["revenue"].sum(), 2) == EXPECTED_REVENUE, "Critical"),
        ("DQ-010", "Profit reconciliation", round(clean["profit"].sum(), 2), EXPECTED_PROFIT, round(clean["profit"].sum(), 2) == EXPECTED_PROFIT, "Critical"),
        ("DQ-011", "Distinct order reconciliation", clean["order_id"].nunique(), EXPECTED_ORDERS, clean["order_id"].nunique() == EXPECTED_ORDERS, "Critical"),
        ("DQ-012", "Returned order reconciliation", returned_orders, EXPECTED_RETURNED_ORDERS, returned_orders == EXPECTED_RETURNED_ORDERS, "High"),
        ("DQ-013", "Revenue arithmetic", round((clean["sales_after_discount"] - clean["return_amount"] - clean["revenue"]).abs().max(), 2), 0.0, bool(((clean["sales_after_discount"] - clean["return_amount"] - clean["revenue"]).abs() < 0.011).all()), "Critical"),
        ("DQ-014", "Profit arithmetic", round((clean["revenue"] - clean["cost_amount"] - clean["profit"]).abs().max(), 2), 0.0, bool(((clean["revenue"] - clean["cost_amount"] - clean["profit"]).abs() < 0.011).all()), "Critical"),
        ("DQ-015", "Rejected row reconciliation", len(rejected), EXPECTED_RAW_ROWS - EXPECTED_CLEAN_ROWS, len(rejected) == EXPECTED_RAW_ROWS - EXPECTED_CLEAN_ROWS, "High"),
    ]
    result = pd.DataFrame(checks, columns=["check_id", "check_name", "actual", "expected", "passed", "severity"])
    result["status"] = result["passed"].map({True: "PASS", False: "FAIL"})
    result["checked_at_utc"] = pd.Timestamp.now(tz="UTC").floor("s").isoformat()
    result.to_csv(QUALITY_CHECKS, index=False)
    rejected.to_csv(REJECTED_RECORDS, index=False)

    summary = {
        "dataset": "Synthetic Indian retail transactions",
        "intended_grain": "one row per order line",
        "raw_rows": int(len(raw)),
        "clean_rows": int(len(clean)),
        "rejected_rows": int(len(rejected)),
        "accepted_rate": round(len(clean) / len(raw), 6),
        "duplicate_rate_raw": round(rejection_counts.get("duplicate_line_id", 0) / len(raw), 6),
        "imputed_rating_rows": int(clean["rating_was_imputed"].sum()),
        "rejection_counts": rejection_counts,
        "checks_passed": int(result["passed"].sum()),
        "checks_total": int(len(result)),
        "overall_status": "READY" if result["passed"].all() else "NEEDS_REVISION",
    }
    QUALITY_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return result

