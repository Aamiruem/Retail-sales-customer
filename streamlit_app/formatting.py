"""Number formatting for Indian business audiences (₹, lakh, crore).

Kept free of Streamlit imports so it can be unit-tested directly.
"""

from __future__ import annotations

import math

LAKH = 100_000
CRORE = 10_000_000


def _is_missing(value) -> bool:
    try:
        return value is None or math.isnan(float(value))
    except (TypeError, ValueError):
        return True


def indian_grouping(value: float, decimals: int = 0) -> str:
    """12345678 -> '1,23,45,678' (Indian digit grouping)."""
    negative = value < 0
    text = f"{abs(value):.{decimals}f}"
    whole, _, fraction = text.partition(".")
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        whole = ",".join(groups + [tail])
    result = f"{whole}.{fraction}" if fraction else whole
    return f"-{result}" if negative else result


def inr(value: float, decimals: int = 0) -> str:
    """Exact rupee amount with Indian grouping: ₹1,23,456."""
    if _is_missing(value):
        return "—"
    return f"₹{indian_grouping(float(value), decimals)}"


def inr_compact(value: float) -> str:
    """Short rupee amount: ₹16.01 Cr, ₹4.08 L, ₹40.8K, ₹950."""
    if _is_missing(value):
        return "—"
    amount = float(value)
    sign = "-" if amount < 0 else ""
    amount = abs(amount)
    if amount >= CRORE:
        return f"{sign}₹{amount / CRORE:,.2f} Cr"
    if amount >= LAKH:
        return f"{sign}₹{amount / LAKH:,.2f} L"
    if amount >= 1_000:
        return f"{sign}₹{amount / 1_000:,.1f}K"
    return f"{sign}₹{amount:,.0f}"


def pct(value: float, decimals: int = 1) -> str:
    """0.2581 -> '25.8%'; missing values (e.g. zero revenue) -> '—'."""
    if _is_missing(value):
        return "—"
    return f"{float(value) * 100:.{decimals}f}%"


def count(value: float) -> str:
    if _is_missing(value):
        return "—"
    return indian_grouping(float(value), 0)


def month_label(year_month: str) -> str:
    """'2024-03' -> 'Mar 24' for compact chart axes."""
    months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    try:
        year, month = str(year_month).split("-")[:2]
        return f"{months[int(month) - 1]} {year[-2:]}"
    except (ValueError, IndexError):
        return str(year_month)
