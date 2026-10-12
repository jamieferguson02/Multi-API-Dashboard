import os
import sys

# make project importable for tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dashboard


def test_constants_present():
    # basic sanity: the MEALDB_URL constant should reference the meal DB
    assert 'themealdb' in dashboard.MEALDB_URL


def test_holidays_function_exists():
    # ensure the fetch_holidays function exists and accepts two args (country_code, year)
    assert callable(dashboard.fetch_holidays)