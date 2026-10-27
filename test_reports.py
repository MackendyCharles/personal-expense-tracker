
import csv

import database
import reports


def test_export_all_transactions(tmp_path, monkeypatch):
    # Use a temporary database and reports directory.
    monkeypatch.setattr(
        database, "DATABASE_NAME", tmp_path / "test.db"
    )
    monkeypatch.setattr(reports, "REPORTS_DIR", tmp_path / "reports")

    database.initialize_database()

    database.insert_transaction(
        "2026-10-10", "expense", "Food", "Lunch", 18.50
    )
    database.insert_transaction(
        "2026-10-15", "income", "Salary", "Pay", 2500.00
    )

    filepath, count = reports.export_transactions_to_csv()

    assert filepath.exists()
    assert count == 2

    with filepath.open(
        "r", newline="", encoding="utf-8-sig"
    ) as csvfile:
        rows = list(csv.DictReader(csvfile))

    assert len(rows) == 2

    # The most recent transaction appears first.
    assert rows[0]["category"] == "Salary"
    assert rows[0]["description"] == "Pay"

    # The older transaction appears second.
    assert rows[1]["category"] == "Food"
    assert rows[1]["description"] == "Lunch"
    assert float(rows[1]["amount"]) == 18.50


def test_export_with_filters(tmp_path, monkeypatch):
    monkeypatch.setattr(
        database, "DATABASE_NAME", tmp_path / "test.db"
    )
    monkeypatch.setattr(reports, "REPORTS_DIR", tmp_path / "reports")

    database.initialize_database()

    database.insert_transaction(
        "2026-10-10", "expense", "Food", "Lunch", 18.50
    )
    database.insert_transaction(
        "2026-10-15", "expense", "Transport", "Bus", 3.00
    )
    database.insert_transaction(
        "2026-11-02", "expense", "Food", "Dinner", 25.00
    )

    filepath, count = reports.export_transactions_to_csv(
        start_date="2026-10-01",
        end_date="2026-10-31",
        category="Food",
    )

    assert count == 1

    with filepath.open(
        "r", newline="", encoding="utf-8-sig"
    ) as csvfile:
        rows = list(csv.DictReader(csvfile))

    assert len(rows) == 1
    assert rows[0]["description"] == "Lunch"


def test_export_empty_database(tmp_path, monkeypatch):
    monkeypatch.setattr(
        database, "DATABASE_NAME", tmp_path / "test.db"
    )
    monkeypatch.setattr(reports, "REPORTS_DIR", tmp_path / "reports")

    database.initialize_database()

    filepath, count = reports.export_transactions_to_csv()

    assert filepath.exists()
    assert count == 0

    with filepath.open(
        "r", newline="", encoding="utf-8-sig"
    ) as csvfile:
        rows = list(csv.DictReader(csvfile))

    assert rows == []
