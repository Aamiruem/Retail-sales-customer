import unittest
from pathlib import Path

from streamlit_app.dashboard_data import (
    apply_filters,
    business_segment_performance,
    calculate_kpis,
    category_performance,
    customer_ml_clusters,
    customer_rfm_profile,
    load_transactions,
    monthly_performance,
    statistical_snapshot,
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

    def test_ml_clusters_and_statistics_are_deterministic(self):
        first_profile, summary = customer_ml_clusters(self.data)
        second_profile, _ = customer_ml_clusters(self.data)
        self.assertTrue(first_profile["ml_cluster"].equals(second_profile["ml_cluster"]))
        self.assertEqual(first_profile["ml_cluster"].nunique(), 4)
        self.assertEqual(int(summary["customers"].sum()), len(first_profile))

        stats = statistical_snapshot(self.data)
        self.assertAlmostEqual(float(stats["return_rate"]), 345 / 3_922)
        self.assertLessEqual(float(stats["return_rate_ci_low"]), float(stats["return_rate"]))
        self.assertGreaterEqual(float(stats["return_rate_ci_high"]), float(stats["return_rate"]))


if __name__ == "__main__":
    unittest.main()
