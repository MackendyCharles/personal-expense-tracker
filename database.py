
import sqlite3
from contextlib import closing
from pathlib import Path

DATABASE_NAME = Path(__file__).with_name("expenses.db")


def get_connection():
    connection = sqlite3.connect(str(DATABASE_NAME))
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with closing(get_connection()) as connection:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    type TEXT NOT NULL
                        CHECK (type IN ('income', 'expense')),
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL CHECK (amount > 0)
                )
            """)


def insert_transaction(
    transaction_date, transaction_type, category, description, amount
):
    with closing(get_connection()) as connection:
        with connection:
            connection.execute(
                """
                INSERT INTO transactions
                    (date, type, category, description, amount)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    transaction_date,
                    transaction_type,
                    category,
                    description,
                    amount,
                ),
            )


def get_all_transactions():
    with closing(get_connection()) as connection:
        rows = connection.execute("""
            SELECT id, date, type, category, description, amount
            FROM transactions
            ORDER BY id DESC
        """).fetchall()

        return [dict(row) for row in rows]


def get_transaction_count():
    with closing(get_connection()) as connection:
        result = connection.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()

        return result[0]


def get_transaction_by_id(transaction_id):
    with closing(get_connection()) as connection:
        row = connection.execute(
            """
            SELECT id, date, type, category, description, amount
            FROM transactions
            WHERE id = ?
            """,
            (transaction_id,),
        ).fetchone()

        return dict(row) if row else None


def update_transaction(
    transaction_id, transaction_type, category, description, amount
):
    if transaction_type not in ("income", "expense"):
        raise ValueError("Type must be income or expense.")
    if not category.strip():
        raise ValueError("Category cannot be empty.")
    if not description.strip():
        raise ValueError("Description cannot be empty.")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute(
                """
                UPDATE transactions
                SET type = ?, category = ?, description = ?, amount = ?
                WHERE id = ?
                """,
                (
                    transaction_type,
                    category.strip(),
                    description.strip(),
                    amount,
                    transaction_id,
                ),
            )

            return cursor.rowcount > 0


def delete_transaction(transaction_id):
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute(
                "DELETE FROM transactions WHERE id = ?",
                (transaction_id,),
            )

            return cursor.rowcount > 0
