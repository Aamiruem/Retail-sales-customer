import sqlite3
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE = PROJECT_ROOT / "data" / "database" / "retail_analytics.db"


class TestHeadlineKPIs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection = sqlite3.connect(DATABASE)

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    def test_headline_reconciliation(self):
        result = self.connection.execute(
            """
            SELECT
                ROUND(SUM(revenue), 2),
                ROUND(SUM(profit), 2),
                SUM(order_flag),
                SUM(return_order_flag)
            FROM fact_sales
            """
        ).fetchone()
        self.assertEqual(result, (160_100_000.0, 41_300_000.0, 3_922, 345))

    def test_rates(self):
        revenue, profit, orders, returned_orders = self.connection.execute(
            "SELECT SUM(revenue), SUM(profit), SUM(order_flag), SUM(return_order_flag) FROM fact_sales"
        ).fetchone()
        self.assertAlmostEqual(profit / revenue, 0.2579637726, places=8)
        self.assertAlmostEqual(returned_orders / orders, 0.0879653238, places=8)

    def test_fact_grain(self):
        rows, unique_lines, orders = self.connection.execute(
            "SELECT COUNT(*), COUNT(DISTINCT line_id), COUNT(DISTINCT order_id) FROM fact_sales"
        ).fetchone()
        self.assertEqual(rows, 4_180)
        self.assertEqual(unique_lines, 4_180)
        self.assertEqual(orders, 3_922)


if __name__ == "__main__":
    unittest.main()

