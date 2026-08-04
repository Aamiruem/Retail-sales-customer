import unittest
from pathlib import Path

from streamlit_app.dashboard_data import (
    apply_filters,
    business_segment_performance,
    calculate_kpis,
    category_performance,
    customer_rfm_profile,
    load_transactions,
    monthly_performance,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestDashboardHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_transactions(PROJECT_ROOT / "data" / "database" / "retail_analytics.db")

    def test_default_filter_returns_complete_data(self):
        filtered = apply_filters(
            self.data,
            (self.data["order_date"].min(), self.data["order_date"].max()),
            [],
            [],
            [],
            [],
        )
        self.assertEqual(len(filtered), 4_180)
        self.assertEqual(calculate_kpis(filtered)["orders"], 3_922)

    def test_single_category_filter(self):
        filtered = apply_filters(
            self.data,
            (self.data["order_date"].min(), self.data["order_date"].max()),
            [],
            ["Electronics"],
            [],
            [],
        )
        self.assertEqual(set(filtered["category"]), {"Electronics"})
        self.assertGreater(len(filtered), 0)

    def test_chart_tables_have_sufficient_density(self):
        self.assertEqual(len(monthly_performance(self.data)), 24)
        self.assertEqual(len(category_performance(self.data)), 5)

    def test_customer_360_tables_are_customer_grain(self):
        profile = customer_rfm_profile(self.data)
        segments = business_segment_performance(self.data)
        self.assertEqual(profile["customer_id"].nunique(), len(profile))
        self.assertGreaterEqual(len(profile), 20)
        self.assertGreaterEqual(len(segments), 3)


if __name__ == "__main__":
    unittest.main()
