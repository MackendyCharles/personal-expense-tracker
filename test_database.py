
import pytest

import database


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Give each test its own temporary database."""

    test_database_path = tmp_path / "test_expenses.db"

    monkeypatch.setattr(
        database, "DATABASE_NAME", test_database_path
    )

    database.initialize_database()
    return test_database_path


def test_insert_and_retrieve_transaction(test_db):
    database.insert_transaction(
        "2026-10-27",
        "expense",
        "Food",
        "Lunch",
        18.50,
    )

    transactions = database.get_all_transactions()

    assert len(transactions) == 1
    assert transactions[0]["category"] == "Food"
    assert transactions[0]["description"] == "Lunch"
    assert transactions[0]["amount"] == pytest.approx(18.50)


def test_transaction_count(test_db):
    database.insert_transaction(
        "2026-10-27", "income", "Salary", "Pay", 2500.00
    )
    database.insert_transaction(
        "2026-10-27", "expense", "Food", "Lunch", 18.50
    )

    assert database.get_transaction_count() == 2


def test_update_transaction(test_db):
    database.insert_transaction(
        "2026-10-27", "expense", "Food", "Lunch", 18.50
    )

    transaction = database.get_all_transactions()[0]

    updated = database.update_transaction(
        transaction["id"],
        "expense",
        "Food",
        "Dinner",
        25.00,
    )

    assert updated is True

    result = database.get_transaction_by_id(transaction["id"])

    assert result["description"] == "Dinner"
    assert result["amount"] == pytest.approx(25.00)


def test_delete_transaction(test_db):
    database.insert_transaction(
        "2026-10-27", "expense", "Food", "Lunch", 18.50
    )

    transaction = database.get_all_transactions()[0]

    deleted = database.delete_transaction(transaction["id"])

    assert deleted is True
    assert database.get_transaction_count() == 0
    assert database.get_transaction_by_id(transaction["id"]) is None


def test_update_missing_transaction(test_db):
    updated = database.update_transaction(
        999, "expense", "Food", "Lunch", 18.50
    )

    assert updated is False


def test_delete_missing_transaction(test_db):
    deleted = database.delete_transaction(999)

    assert deleted is False


@pytest.mark.parametrize("amount", [0, -10])
def test_update_rejects_invalid_amount(test_db, amount):
    database.insert_transaction(
        "2026-10-27", "expense", "Food", "Lunch", 18.50
    )

    transaction = database.get_all_transactions()[0]

    with pytest.raises(ValueError):
        database.update_transaction(
            transaction["id"],
            "expense",
            "Food",
            "Lunch",
            amount,
        )

    result = database.get_transaction_by_id(transaction["id"])
    assert result["amount"] == pytest.approx(18.50)
