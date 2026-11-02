"""Smoke tests: every dashboard page renders without errors, including edge-case filters."""

import datetime as dt
import unittest
import warnings
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "streamlit_app" / "app.py")
PAGES = [
    "🏠 Home",
    "📈 Executive Overview",
    "👥 Customer Intelligence",
    "🛍️ Products & Returns",
    "🛡️ Data Quality",
    "🧰 Project & Technology",
]


def run_app(**state) -> AppTest:
    warnings.filterwarnings("ignore")
    app = AppTest.from_file(APP, default_timeout=180)
    for key, value in state.items():
        app.session_state[key] = value
    app.run()
    return app


class TestAppPages(unittest.TestCase):
    def test_every_page_renders(self):
        for page in PAGES:
            with self.subTest(page=page):
                app = run_app(dashboard_page=page)
                self.assertEqual(len(app.exception), 0, [error.value for error in app.exception])

    def test_single_day_and_narrow_filters(self):
        narrow = {
            "filter_dates": (dt.date(2024, 3, 5), dt.date(2024, 3, 5)),
            "filter_regions": ["West"],
        }
        for page in PAGES:
            with self.subTest(page=page):
                app = run_app(dashboard_page=page, **narrow)
                self.assertEqual(len(app.exception), 0, [error.value for error in app.exception])

    def test_no_matching_rows_shows_friendly_message(self):
        app = run_app(
            filter_dates=(dt.date(2024, 1, 1), dt.date(2024, 1, 1)),
            filter_regions=["West"],
            filter_categories=["Fashion"],
            filter_channels=["Marketplace"],
        )
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("No transactions match" in warning.value for warning in app.warning))

    def test_target_caveat_when_scoped(self):
        app = run_app(filter_regions=["West"], dashboard_page="📈 Executive Overview")
        markdown = " ".join(block.value for block in app.markdown)
        self.assertIn("Targets are set for the whole company", markdown)

    def test_home_shows_insights_and_comparison(self):
        app = run_app(filter_dates=(dt.date(2025, 1, 1), dt.date(2025, 12, 31)))
        markdown = " ".join(block.value for block in app.markdown)
        self.assertIn("Key insights", markdown)
        self.assertIn("vs prev. period", markdown)
        self.assertEqual(len(app.exception), 0)


if __name__ == "__main__":
    unittest.main()
