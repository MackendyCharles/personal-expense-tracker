
import calendar
from datetime import date

import database


def generate_monthly_report(year, month):
    """Calculate income, expenses, balance, and spending by category."""

    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12.")

    if year < 1 or year > 9999:
        raise ValueError("Year must be between 1 and 9999.")

    start_date = date(year, month, 1).isoformat()

    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day).isoformat()

    transactions = database.get_filtered_transactions(
        start_date=start_date,
        end_date=end_date,
    )

    total_income = sum(
        t["amount"]
        for t in transactions
        if t["type"] == "income"
    )

    total_expenses = sum(
        t["amount"]
        for t in transactions
        if t["type"] == "expense"
    )

    spending_by_category = {}

    for transaction in transactions:
        if transaction["type"] == "expense":
            category = transaction["category"]

            spending_by_category[category] = (
                spending_by_category.get(category, 0)
                + transaction["amount"]
            )

    return {
        "year": year,
        "month": month,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": total_income - total_expenses,
        "spending_by_category": dict(
            sorted(spending_by_category.items())
        ),
        "transaction_count": len(transactions),
    }
