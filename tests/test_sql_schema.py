import sqlite3
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE = PROJECT_ROOT / "data" / "database" / "retail_analytics.db"


class TestStarSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection = sqlite3.connect(DATABASE)
        cls.connection.execute("PRAGMA foreign_keys = ON")

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    def test_required_tables_exist(self):
        tables = {row[0] for row in self.connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        required = {"fact_sales", "dim_date", "dim_customer", "dim_product", "dim_store", "monthly_targets", "customer_rfm"}
        self.assertTrue(required.issubset(tables))

    def test_foreign_keys(self):
        violations = self.connection.execute("PRAGMA foreign_key_check").fetchall()
        self.assertEqual(violations, [])

    def test_join_does_not_multiply_rows(self):
        fact_rows = self.connection.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
        view_rows = self.connection.execute("SELECT COUNT(*) FROM vw_sales_enriched").fetchone()[0]
        self.assertEqual(fact_rows, view_rows)

    def test_dimension_key_uniqueness(self):
        for table, key in [
            ("dim_date", "date_key"),
            ("dim_customer", "customer_key"),
            ("dim_product", "product_key"),
            ("dim_store", "store_key"),
        ]:
            rows, keys = self.connection.execute(f"SELECT COUNT(*), COUNT(DISTINCT {key}) FROM {table}").fetchone()
            self.assertEqual(rows, keys)


if __name__ == "__main__":
    unittest.main()

