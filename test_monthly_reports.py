
import pytest

import database
import monthly_reports


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Create an isolated database for each test."""

    monkeypatch.setattr(
        database,
        "DATABASE_NAME",
        tmp_path / "monthly_test.db",
    )

    database.initialize_database()

    return tmp_path / "monthly_test.db"


def test_monthly_totals_and_category_spending(test_db):
    database.insert_transaction(
        "2026-10-01", "income", "Salary", "Pay", 3000.00
    )
    database.insert_transaction(
        "2026-10-05", "expense", "Food", "Groceries", 150.00
    )
    database.insert_transaction(
        "2026-10-10", "expense", "Food", "Restaurant", 50.00
    )
    database.insert_transaction(
        "2026-10-15", "expense", "Rent", "Monthly rent", 900.00
    )

    # This transaction must not be included in October.
    database.insert_transaction(
        "2026-11-01", "expense", "Food", "November groceries", 75.00
    )

    report = monthly_reports.generate_monthly_report(2026, 10)

    assert report["total_income"] == pytest.approx(3000.00)
    assert report["total_expenses"] == pytest.approx(1100.00)
    assert report["balance"] == pytest.approx(1900.00)

    assert report["spending_by_category"]["Food"] == pytest.approx(200.00)
    assert report["spending_by_category"]["Rent"] == pytest.approx(900.00)

    assert report["transaction_count"] == 4


def test_month_without_transactions(test_db):
    report = monthly_reports.generate_monthly_report(2026, 9)

    assert report["total_income"] == 0
    assert report["total_expenses"] == 0
    assert report["balance"] == 0
    assert report["spending_by_category"] == {}
    assert report["transaction_count"] == 0


def test_report_handles_leap_year_february(test_db):
    database.insert_transaction(
        "2024-02-29", "expense", "Food", "Leap day meal", 20.00
    )

    report = monthly_reports.generate_monthly_report(2024, 2)

    assert report["total_expenses"] == pytest.approx(20.00)
    assert report["transaction_count"] == 1


@pytest.mark.parametrize("month", [0, 13, -1])
def test_invalid_month_is_rejected(test_db, month):
    with pytest.raises(ValueError):
        monthly_reports.generate_monthly_report(2026, month)
