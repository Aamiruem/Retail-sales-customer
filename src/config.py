from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DATABASE_DIR = DATA_DIR / "database"
QUALITY_DIR = DATA_DIR / "quality"
REPORTS_DIR = PROJECT_ROOT / "reports"
CHARTS_DIR = REPORTS_DIR / "charts"

RAW_CSV = RAW_DIR / "retail_sales_source_a.csv"
RAW_EXCEL = RAW_DIR / "retail_sales_source_b.xlsx"
RAW_EXCEL_STAGING = RAW_DIR / "retail_sales_source_b_staging.json"
RAW_SQLITE = RAW_DIR / "retail_sales_source_c.db"

CLEAN_TRANSACTIONS = PROCESSED_DIR / "retail_transactions_clean.csv"
FACT_SALES_CSV = PROCESSED_DIR / "fact_sales.csv"
DIM_DATE_CSV = PROCESSED_DIR / "dim_date.csv"
DIM_CUSTOMER_CSV = PROCESSED_DIR / "dim_customer.csv"
DIM_PRODUCT_CSV = PROCESSED_DIR / "dim_product.csv"
DIM_STORE_CSV = PROCESSED_DIR / "dim_store.csv"
MONTHLY_TARGETS_CSV = PROCESSED_DIR / "monthly_targets.csv"
RFM_SEGMENTS_CSV = PROCESSED_DIR / "customer_rfm_segments.csv"
EXCEL_PAYLOAD = PROCESSED_DIR / "excel_dashboard_payload.json"

ANALYTICS_DB = DATABASE_DIR / "retail_analytics.db"
REJECTED_RECORDS = QUALITY_DIR / "rejected_records.csv"
QUALITY_CHECKS = QUALITY_DIR / "data_quality_checks.csv"
QUALITY_SUMMARY = QUALITY_DIR / "data_quality_summary.json"
GENERATION_MANIFEST = QUALITY_DIR / "generation_manifest.json"

EXPECTED_RAW_ROWS = 4_224
EXPECTED_CLEAN_ROWS = 4_180
EXPECTED_ORDERS = 3_922
EXPECTED_RETURNED_ORDERS = 345
EXPECTED_REVENUE = 160_100_000.00
EXPECTED_PROFIT = 41_300_000.00
EXPECTED_MARGIN = EXPECTED_PROFIT / EXPECTED_REVENUE


def ensure_directories() -> None:
    for path in (RAW_DIR, PROCESSED_DIR, DATABASE_DIR, QUALITY_DIR, REPORTS_DIR, CHARTS_DIR):
        path.mkdir(parents=True, exist_ok=True)

