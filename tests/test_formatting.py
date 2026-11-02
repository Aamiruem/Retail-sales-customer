import math
import unittest

from streamlit_app.formatting import count, indian_grouping, inr, inr_compact, month_label, pct


class TestFormatting(unittest.TestCase):
    def test_indian_grouping(self):
        self.assertEqual(indian_grouping(999), "999")
        self.assertEqual(indian_grouping(1_000), "1,000")
        self.assertEqual(indian_grouping(123_456), "1,23,456")
        self.assertEqual(indian_grouping(12_345_678), "1,23,45,678")
        self.assertEqual(indian_grouping(-40_821), "-40,821")

    def test_rupee_amounts(self):
        self.assertEqual(inr(40_821.4), "₹40,821")
        self.assertEqual(inr_compact(160_100_000), "₹16.01 Cr")
        self.assertEqual(inr_compact(9_050_000), "₹90.50 L")
        self.assertEqual(inr_compact(40_821), "₹40.8K")
        self.assertEqual(inr_compact(950), "₹950")
        self.assertEqual(inr_compact(-250_000), "-₹2.50 L")

    def test_missing_values_never_show_nan(self):
        for formatter in (inr, inr_compact, pct, count):
            self.assertEqual(formatter(math.nan), "—")
            self.assertEqual(formatter(None), "—")

    def test_percent_and_month(self):
        self.assertEqual(pct(0.2581), "25.8%")
        self.assertEqual(month_label("2024-03"), "Mar 24")
        self.assertEqual(month_label("bad"), "bad")


if __name__ == "__main__":
    unittest.main()
