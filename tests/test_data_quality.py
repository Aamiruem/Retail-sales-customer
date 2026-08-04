import json
import unittest
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestDataQuality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads((PROJECT_ROOT / "data" / "quality" / "data_quality_summary.json").read_text(encoding="utf-8"))
        cls.checks = pd.read_csv(PROJECT_ROOT / "data" / "quality" / "data_quality_checks.csv")
        cls.rejected = pd.read_csv(PROJECT_ROOT / "data" / "quality" / "rejected_records.csv")

    def test_quality_status_ready(self):
        self.assertEqual(self.summary["overall_status"], "READY")
        self.assertTrue(self.checks["passed"].all())
        self.assertEqual(len(self.checks), 15)

    def test_rejection_reconciliation(self):
        expected = {
            "duplicate_line_id": 10,
            "missing_customer_id": 8,
            "invalid_date": 8,
            "non_positive_quantity": 6,
            "invalid_discount": 6,
            "invalid_product_id": 6,
        }
        self.assertEqual(self.rejected["rejection_reason"].value_counts().to_dict(), expected)
        self.assertEqual(len(self.rejected), 44)

    def test_clean_extract_domain_rules(self):
        clean = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "retail_transactions_clean.csv")
        self.assertTrue(clean["line_id"].is_unique)
        self.assertTrue(clean["quantity"].gt(0).all())
        self.assertTrue(clean["discount_pct"].between(0, 0.60).all())
        self.assertFalse(clean[["line_id", "order_id", "customer_id", "product_id"]].isna().any().any())


if __name__ == "__main__":
    unittest.main()

