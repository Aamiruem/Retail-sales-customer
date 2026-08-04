"""Generate deterministic synthetic retail data across CSV, Excel staging and SQLite.

The generator deliberately inserts 44 isolated quality issues into 4,224 raw
rows. The 4,180 valid transaction lines reconcile exactly to the headline KPIs
used in the portfolio project.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from src.config import (
    EXPECTED_CLEAN_ROWS,
    EXPECTED_ORDERS,
    EXPECTED_PROFIT,
    EXPECTED_RAW_ROWS,
    EXPECTED_RETURNED_ORDERS,
    EXPECTED_REVENUE,
    GENERATION_MANIFEST,
    RAW_CSV,
    RAW_EXCEL_STAGING,
    RAW_SQLITE,
    ensure_directories,
)


SEED = 20260804


@dataclass(frozen=True)
class Location:
    region: str
    state: str
    city: str


LOCATIONS = [
    Location("North", "Delhi", "New Delhi"),
    Location("North", "Uttar Pradesh", "Lucknow"),
    Location("North", "Punjab", "Chandigarh"),
    Location("South", "Karnataka", "Bengaluru"),
    Location("South", "Tamil Nadu", "Chennai"),
    Location("South", "Telangana", "Hyderabad"),
    Location("East", "West Bengal", "Kolkata"),
    Location("East", "Bihar", "Patna"),
    Location("East", "Odisha", "Bhubaneswar"),
    Location("West", "Maharashtra", "Mumbai"),
    Location("West", "Gujarat", "Ahmedabad"),
    Location("West", "Rajasthan", "Jaipur"),
    Location("Central", "Madhya Pradesh", "Indore"),
    Location("Central", "Chhattisgarh", "Raipur"),
]


PRODUCTS = {
    "Electronics": [
        ("Smartphones", "Nova 5G Smartphone"),
        ("Laptops", "Apex Pro Laptop"),
        ("Accessories", "Wireless Earbuds"),
        ("Accessories", "Smart Fitness Watch"),
        ("Television", "Ultra HD Smart TV"),
        ("Tablets", "StudyPad Tablet"),
        ("Accessories", "Noise-Cancel Headphones"),
        ("Cameras", "Mirrorless Camera"),
        ("Accessories", "Portable SSD"),
        ("Audio", "Bluetooth Speaker"),
    ],
    "Home & Kitchen": [
        ("Appliances", "Frost-Free Refrigerator"),
        ("Appliances", "Front-Load Washer"),
        ("Appliances", "Convection Microwave"),
        ("Cookware", "Premium Cookware Set"),
        ("Furniture", "Ergonomic Office Chair"),
        ("Furniture", "Modular Study Desk"),
        ("Appliances", "Air Purifier"),
        ("Appliances", "Mixer Grinder"),
        ("Home Decor", "Designer Floor Lamp"),
        ("Bedding", "Memory Foam Mattress"),
    ],
    "Fashion": [
        ("Clothing", "Classic Formal Shirt"),
        ("Clothing", "Denim Jacket"),
        ("Footwear", "Running Shoes"),
        ("Footwear", "Leather Office Shoes"),
        ("Bags", "Travel Backpack"),
        ("Bags", "Premium Handbag"),
        ("Clothing", "Winter Hoodie"),
        ("Clothing", "Ethnic Kurta Set"),
        ("Accessories", "Polarized Sunglasses"),
        ("Accessories", "Leather Wallet"),
    ],
    "Beauty & Personal Care": [
        ("Skincare", "Vitamin C Skin Serum"),
        ("Skincare", "Hydrating Face Cream"),
        ("Grooming", "Professional Hair Dryer"),
        ("Grooming", "Cordless Grooming Kit"),
        ("Wellness", "Aroma Wellness Set"),
        ("Skincare", "Daily Sunscreen SPF50"),
        ("Haircare", "Keratin Haircare Pack"),
        ("Fragrance", "Signature Perfume"),
        ("Wellness", "Electric Massager"),
        ("Cosmetics", "Makeup Essentials Kit"),
    ],
    "Sports & Outdoors": [
        ("Fitness", "Adjustable Dumbbell Set"),
        ("Fitness", "Premium Yoga Mat"),
        ("Outdoor", "All-Weather Camping Tent"),
        ("Sportswear", "Performance Track Suit"),
        ("Cycling", "Urban Hybrid Bicycle"),
        ("Fitness", "Foldable Treadmill"),
        ("Cricket", "Professional Cricket Kit"),
        ("Outdoor", "Trekking Backpack"),
        ("Sports", "Badminton Racquet Set"),
        ("Fitness", "Resistance Training Kit"),
    ],
}


CATEGORY_BASE_PRICE = {
    "Electronics": 24_000,
    "Home & Kitchen": 19_000,
    "Fashion": 7_500,
    "Beauty & Personal Care": 5_500,
    "Sports & Outdoors": 11_000,
}

CATEGORY_COST_RATIO = {
    "Electronics": 0.78,
    "Home & Kitchen": 0.74,
    "Fashion": 0.62,
    "Beauty & Personal Care": 0.58,
    "Sports & Outdoors": 0.67,
}


def _product_catalog() -> pd.DataFrame:
    rows: list[dict] = []
    product_number = 1
    for category, products in PRODUCTS.items():
        for subcategory, product_name in products:
            rows.append(
                {
                    "product_id": f"P{product_number:03d}",
                    "product_name": product_name,
                    "category": category,
                    "subcategory": subcategory,
                }
            )
            product_number += 1
    return pd.DataFrame(rows)


def _customer_catalog(rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    segments = np.array(["Consumer", "Corporate", "Home Office"])
    segment_probabilities = np.array([0.56, 0.26, 0.18])
    for customer_number in range(1, 1_201):
        location = LOCATIONS[int(rng.integers(0, len(LOCATIONS)))]
        rows.append(
            {
                "customer_id": f"C{customer_number:04d}",
                "customer_name": f"Customer {customer_number:04d}",
                "customer_segment": str(rng.choice(segments, p=segment_probabilities)),
                "region": location.region,
                "state": location.state,
                "city": location.city,
            }
        )
    return pd.DataFrame(rows)


def _order_dates(rng: np.random.Generator, count: int) -> pd.DatetimeIndex:
    all_dates = pd.date_range("2024-01-01", "2025-12-31", freq="D")
    month_weights = {
        1: 0.85,
        2: 0.82,
        3: 0.94,
        4: 0.92,
        5: 0.98,
        6: 0.96,
        7: 1.00,
        8: 1.04,
        9: 1.10,
        10: 1.28,
        11: 1.34,
        12: 1.42,
    }
    weights = np.array([month_weights[d.month] for d in all_dates], dtype=float)
    weights /= weights.sum()
    selected = rng.choice(all_dates.to_numpy(), size=count, replace=True, p=weights)
    return pd.DatetimeIndex(selected)


def _build_valid_transactions(rng: np.random.Generator) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    products = _product_catalog()
    customers = _customer_catalog(rng)
    order_ids = [f"O{order_number:06d}" for order_number in range(1, EXPECTED_ORDERS + 1)]

    eligible_for_multi = np.arange(EXPECTED_ORDERS - 1)
    two_line_order_positions = set(rng.choice(eligible_for_multi, size=258, replace=False).tolist())
    return_order_positions = set(rng.choice(eligible_for_multi, size=EXPECTED_RETURNED_ORDERS, replace=False).tolist())
    order_dates = _order_dates(rng, EXPECTED_ORDERS)

    line_rows: list[dict] = []
    line_number = 1
    for order_position, order_id in enumerate(order_ids):
        customer = customers.iloc[int(rng.integers(0, len(customers)))]
        category = str(rng.choice(list(PRODUCTS), p=[0.27, 0.23, 0.18, 0.14, 0.18]))
        category_products = products[products["category"] == category]
        channel = str(rng.choice(["Online", "Retail Store", "Marketplace"], p=[0.48, 0.34, 0.18]))
        payment_method = str(
            rng.choice(["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash"], p=[0.36, 0.24, 0.18, 0.12, 0.10])
        )
        store_id = "STORE-ONLINE" if channel != "Retail Store" else f"STORE-{int(rng.integers(1, 21)):02d}"
        line_count = 2 if order_position in two_line_order_positions else 1
        is_returned = order_position in return_order_positions
        order_date = pd.Timestamp(order_dates[order_position])
        ship_days = int(rng.integers(1, 8))

        for _ in range(line_count):
            product = category_products.iloc[int(rng.integers(0, len(category_products)))]
            quantity = int(rng.choice([1, 2, 3, 4, 5], p=[0.42, 0.29, 0.16, 0.08, 0.05]))
            unit_price = CATEGORY_BASE_PRICE[category] * float(rng.uniform(0.55, 1.75))
            discount_pct = float(rng.choice([0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30], p=[0.18, 0.17, 0.23, 0.18, 0.13, 0.07, 0.04]))
            rating = float(rng.choice([1, 2, 3, 4, 5], p=[0.03, 0.06, 0.16, 0.37, 0.38]))
            if rng.random() < 0.012:
                rating = np.nan

            line_rows.append(
                {
                    "line_id": f"L{line_number:07d}",
                    "order_id": order_id,
                    "order_date": order_date.strftime("%Y-%m-%d"),
                    "ship_date": (order_date + pd.Timedelta(days=ship_days)).strftime("%Y-%m-%d"),
                    "customer_id": customer["customer_id"],
                    "customer_name": customer["customer_name"],
                    "customer_segment": customer["customer_segment"],
                    "region": customer["region"],
                    "state": customer["state"],
                    "city": customer["city"],
                    "store_id": store_id,
                    "channel": channel,
                    "product_id": product["product_id"],
                    "product_name": product["product_name"],
                    "category": product["category"],
                    "subcategory": product["subcategory"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "discount_pct": discount_pct,
                    "return_flag": int(is_returned),
                    "payment_method": payment_method,
                    "rating": rating,
                }
            )
            line_number += 1

    transactions = pd.DataFrame(line_rows)
    assert len(transactions) == EXPECTED_CLEAN_ROWS

    # Reserve the last line as an exact balancing row.
    transactions.loc[transactions.index[-1], ["quantity", "discount_pct", "return_flag"]] = [1, 0.0, 0]

    provisional_gross = transactions["unit_price"] * transactions["quantity"]
    provisional_net = provisional_gross * (1.0 - transactions["discount_pct"]) * (1 - transactions["return_flag"])
    price_scale = EXPECTED_REVENUE / provisional_net.sum()
    transactions["unit_price"] = (transactions["unit_price"] * price_scale).round(2)

    transactions["gross_sales"] = (transactions["unit_price"] * transactions["quantity"]).round(2)
    transactions["discount_amount"] = (transactions["gross_sales"] * transactions["discount_pct"]).round(2)
    transactions["sales_after_discount"] = (transactions["gross_sales"] - transactions["discount_amount"]).round(2)
    transactions["return_amount"] = (transactions["sales_after_discount"] * transactions["return_flag"]).round(2)
    transactions["revenue"] = (transactions["sales_after_discount"] - transactions["return_amount"]).round(2)

    revenue_residual = round(EXPECTED_REVENUE - transactions["revenue"].sum(), 2)
    last_index = transactions.index[-1]
    transactions.loc[last_index, "unit_price"] = round(transactions.loc[last_index, "unit_price"] + revenue_residual, 2)
    transactions.loc[last_index, "gross_sales"] = transactions.loc[last_index, "unit_price"]
    transactions.loc[last_index, "discount_amount"] = 0.0
    transactions.loc[last_index, "sales_after_discount"] = transactions.loc[last_index, "gross_sales"]
    transactions.loc[last_index, "return_amount"] = 0.0
    transactions.loc[last_index, "revenue"] = transactions.loc[last_index, "gross_sales"]

    ratio_noise = rng.normal(0, 0.025, len(transactions))
    base_ratio = transactions["category"].map(CATEGORY_COST_RATIO).astype(float) + ratio_noise
    base_cost = np.where(
        transactions["return_flag"].eq(1),
        transactions["sales_after_discount"] * 0.12,
        transactions["gross_sales"] * base_ratio.clip(0.50, 0.86),
    )
    target_cost = EXPECTED_REVENUE - EXPECTED_PROFIT
    transactions["cost_amount"] = (base_cost * (target_cost / base_cost.sum())).round(2)
    cost_residual = round(target_cost - transactions["cost_amount"].sum(), 2)
    transactions.loc[last_index, "cost_amount"] = round(transactions.loc[last_index, "cost_amount"] + cost_residual, 2)
    transactions["unit_cost"] = (transactions["cost_amount"] / transactions["quantity"]).round(2)
    transactions["profit"] = (transactions["revenue"] - transactions["cost_amount"]).round(2)

    assert round(transactions["revenue"].sum(), 2) == EXPECTED_REVENUE
    assert round(transactions["profit"].sum(), 2) == EXPECTED_PROFIT
    assert transactions["order_id"].nunique() == EXPECTED_ORDERS
    assert transactions.loc[transactions["return_flag"].eq(1), "order_id"].nunique() == EXPECTED_RETURNED_ORDERS
    return transactions, products, customers


def _add_quality_issues(valid: pd.DataFrame, products: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    issue_frames: list[pd.DataFrame] = []
    sampled_indices = rng.choice(valid.index.to_numpy(), size=44, replace=False)
    cursor = 0

    duplicates = valid.loc[sampled_indices[cursor : cursor + 10]].copy()
    issue_frames.append(duplicates)
    cursor += 10

    missing_customer = valid.loc[sampled_indices[cursor : cursor + 8]].copy()
    missing_customer["line_id"] = [f"BAD-MISSING-CUST-{i:02d}" for i in range(1, 9)]
    missing_customer["order_id"] = [f"BAD-ORDER-MC-{i:02d}" for i in range(1, 9)]
    missing_customer["customer_id"] = None
    issue_frames.append(missing_customer)
    cursor += 8

    invalid_dates = valid.loc[sampled_indices[cursor : cursor + 8]].copy()
    invalid_dates["line_id"] = [f"BAD-DATE-{i:02d}" for i in range(1, 9)]
    invalid_dates["order_id"] = [f"BAD-ORDER-DATE-{i:02d}" for i in range(1, 9)]
    invalid_dates["order_date"] = "not-a-date"
    issue_frames.append(invalid_dates)
    cursor += 8

    negative_quantity = valid.loc[sampled_indices[cursor : cursor + 6]].copy()
    negative_quantity["line_id"] = [f"BAD-QTY-{i:02d}" for i in range(1, 7)]
    negative_quantity["order_id"] = [f"BAD-ORDER-QTY-{i:02d}" for i in range(1, 7)]
    negative_quantity["quantity"] = -1
    issue_frames.append(negative_quantity)
    cursor += 6

    invalid_discount = valid.loc[sampled_indices[cursor : cursor + 6]].copy()
    invalid_discount["line_id"] = [f"BAD-DISCOUNT-{i:02d}" for i in range(1, 7)]
    invalid_discount["order_id"] = [f"BAD-ORDER-DISC-{i:02d}" for i in range(1, 7)]
    invalid_discount["discount_pct"] = 1.50
    issue_frames.append(invalid_discount)
    cursor += 6

    invalid_product = valid.loc[sampled_indices[cursor : cursor + 6]].copy()
    invalid_product["line_id"] = [f"BAD-PRODUCT-{i:02d}" for i in range(1, 7)]
    invalid_product["order_id"] = [f"BAD-ORDER-PROD-{i:02d}" for i in range(1, 7)]
    invalid_product["product_id"] = "P-UNKNOWN"
    invalid_product["product_name"] = "Unknown Product"
    invalid_product["category"] = "Unknown"
    issue_frames.append(invalid_product)

    raw = pd.concat([valid, *issue_frames], ignore_index=True)
    raw = raw.sample(frac=1, random_state=SEED).reset_index(drop=True)
    assert len(raw) == EXPECTED_RAW_ROWS
    assert set(products["product_id"]).issuperset(set(valid["product_id"]))
    return raw


def generate() -> None:
    ensure_directories()
    rng = np.random.default_rng(SEED)
    valid, products, customers = _build_valid_transactions(rng)
    raw = _add_quality_issues(valid, products, rng)

    split_points = (2_112, 3_168)
    source_a = raw.iloc[: split_points[0]].copy()
    source_b = raw.iloc[split_points[0] : split_points[1]].copy()
    source_c = raw.iloc[split_points[1] :].copy()

    source_a["source_system"] = "CSV"
    source_b["source_system"] = "EXCEL"
    source_c["source_system"] = "SQLITE"
    ingestion_ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    for frame in (source_a, source_b, source_c):
        frame["ingestion_ts"] = ingestion_ts

    source_a.to_csv(RAW_CSV, index=False)
    RAW_EXCEL_STAGING.write_text(source_b.to_json(orient="records", indent=2), encoding="utf-8")

    if RAW_SQLITE.exists():
        RAW_SQLITE.unlink()
    with sqlite3.connect(RAW_SQLITE) as connection:
        source_c.to_sql("raw_sales", connection, index=False, if_exists="replace")
        connection.execute("CREATE INDEX idx_raw_sales_line_id ON raw_sales(line_id)")

    manifest = {
        "dataset_type": "synthetic",
        "seed": SEED,
        "generated_at_utc": ingestion_ts,
        "raw_rows": int(len(raw)),
        "expected_clean_rows": EXPECTED_CLEAN_ROWS,
        "raw_source_rows": {"csv": len(source_a), "excel": len(source_b), "sqlite": len(source_c)},
        "quality_issues_inserted": {
            "duplicate_line_id": 10,
            "missing_customer_id": 8,
            "invalid_order_date": 8,
            "non_positive_quantity": 6,
            "invalid_discount": 6,
            "invalid_product": 6,
        },
        "expected_kpis": {
            "revenue": EXPECTED_REVENUE,
            "profit": EXPECTED_PROFIT,
            "profit_margin": round(EXPECTED_PROFIT / EXPECTED_REVENUE, 6),
            "orders": EXPECTED_ORDERS,
            "returned_orders": EXPECTED_RETURNED_ORDERS,
            "return_rate": round(EXPECTED_RETURNED_ORDERS / EXPECTED_ORDERS, 6),
        },
    }
    GENERATION_MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Generated {len(raw):,} raw rows across CSV, Excel staging, and SQLite.")
    print(f"Valid KPI base: {len(valid):,} lines, {valid['order_id'].nunique():,} orders.")


if __name__ == "__main__":
    generate()
