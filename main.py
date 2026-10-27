import csv
from datetime import date
import reports
import database
import monthly_reports


def add_transaction(transaction_type, category, description, amount):
    """Validate and save a new transaction."""

    if transaction_type not in ("income", "expense"):
        raise ValueError("Type must be income or expense.")
    if not category.strip():
        raise ValueError("Category cannot be empty.")
    if not description.strip():
        raise ValueError("Description cannot be empty.")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    database.insert_transaction(
        date.today().isoformat(),
        transaction_type,
        category.strip(),
        description.strip(),
        amount,
    )


def display_transactions():
    transactions = database.get_all_transactions()

    print(f"\nTotal transactions: {len(transactions)}")

    if not transactions:
        print("No transactions recorded yet.")
        return

    print("\n--- TRANSACTION HISTORY ---")

    for t in transactions:
        print(
            f'ID: {t["id"]} | {t["date"]} | '
            f'{t["type"].upper()} | {t["category"]} | '
            f'{t["description"]} | ${t["amount"]:.2f}'
        )


def display_summary():
    transactions = database.get_all_transactions()

    income = sum(
        t["amount"] for t in transactions
        if t["type"] == "income"
    )
    expenses = sum(
        t["amount"] for t in transactions
        if t["type"] == "expense"
    )

    print("\n--- FINANCIAL SUMMARY ---")
    print(f"Total income:   ${income:.2f}")
    print(f"Total expenses: ${expenses:.2f}")
    print(f"Balance:        ${income - expenses:.2f}")


def edit_transaction():
    """Ask the user which transaction to edit."""

    display_transactions()

    try:
        transaction_id = int(input("Enter transaction ID to edit: "))
    except ValueError:
        print("Invalid ID. Please enter a whole number.")
        return

    transaction = database.get_transaction_by_id(transaction_id)

    if transaction is None:
        print("Transaction not found.")
        return

    print("Press Enter to keep an existing value.")

    transaction_type = input(
        f'Type (income/expense) [{transaction["type"]}]: '
    ).strip().lower() or transaction["type"]

    category = input(
        f'Category [{transaction["category"]}]: '
    ).strip() or transaction["category"]

    description = input(
        f'Description [{transaction["description"]}]: '
    ).strip() or transaction["description"]

    amount_text = input(
        f'Amount [{transaction["amount"]:.2f}]: '
    ).strip()

    try:
        amount = (
            float(amount_text)
            if amount_text
            else transaction["amount"]
        )

        updated = database.update_transaction(
            transaction_id,
            transaction_type,
            category,
            description,
            amount,
        )

        if updated:
            print("Transaction updated successfully!")
        else:
            print("Transaction not found.")

    except ValueError as error:
        print(f"Invalid input: {error}")


def remove_transaction():
    """Delete a transaction by its ID."""

    display_transactions()

    try:
        transaction_id = int(input("Enter transaction ID to delete: "))
    except ValueError:
        print("Invalid ID. Please enter a whole number.")
        return

    transaction = database.get_transaction_by_id(transaction_id)

    if transaction is None:
        print("Transaction not found.")
        return

    confirmation = input(
        f'Delete "{transaction["description"]}"? (y/n): '
    ).strip().lower()

    if confirmation == "y":
        if database.delete_transaction(transaction_id):
            print("Transaction deleted successfully!")
        else:
            print("Transaction not found.")
    else:
        print("Deletion cancelled.")


def filter_transactions():
    """Filter transactions by date range and category."""

    print("\n--- FILTER TRANSACTIONS ---")
    print("Leave a field empty to skip that filter.")

    start_date = input("Start date (YYYY-MM-DD): ").strip()
    end_date = input("End date (YYYY-MM-DD): ").strip()
    category = input("Category: ").strip()

    try:
        if start_date:
            date.fromisoformat(start_date)

        if end_date:
            date.fromisoformat(end_date)

        if start_date and end_date and start_date > end_date:
            print("Error: start date must not be after end date.")
            return

    except ValueError:
        print("Invalid date. Use the format YYYY-MM-DD.")
        return

    transactions = database.get_filtered_transactions(
        start_date=start_date or None,
        end_date=end_date or None,
        category=category or None,
    )

    print(f"\nMatching transactions: {len(transactions)}")

    if not transactions:
        print("No matching transactions found.")
        return

    for t in transactions:
        print(
            f'ID: {t["id"]} | {t["date"]} | '
            f'{t["type"].upper()} | {t["category"]} | '
            f'{t["description"]} | ${t["amount"]:.2f}'
        )


def export_csv_report():
    """Ask for optional filters and export matching transactions."""

    print("\n--- EXPORT CSV REPORT ---")
    print("Leave a field empty to skip that filter.")

    start_date = input("Start date (YYYY-MM-DD): ").strip()
    end_date = input("End date (YYYY-MM-DD): ").strip()
    category = input("Category: ").strip()

    try:
        if start_date:
            date.fromisoformat(start_date)

        if end_date:
            date.fromisoformat(end_date)

        if start_date and end_date and start_date > end_date:
            print("Error: start date must not be after end date.")
            return

    except ValueError:
        print("Invalid date. Use the format YYYY-MM-DD.")
        return

    try:
        filepath, count = reports.export_transactions_to_csv(
            start_date=start_date or None,
            end_date=end_date or None,
            category=category or None,
        )

        print(f"CSV report exported successfully!")
        print(f"Transactions exported: {count}")
        print(f"File location: {filepath.resolve()}")

    except (OSError, csv.Error) as error:
        print(f"Could not export report: {error}")


def display_monthly_report():
    """Ask for a month and display its financial report."""

    print("\n--- MONTHLY SPENDING REPORT ---")

    try:
        year = int(input("Enter year (e.g. 2026): ").strip())
        month = int(input("Enter month (1-12): ").strip())

        report = monthly_reports.generate_monthly_report(year, month)

    except ValueError as error:
        print(f"Invalid input: {error}")
        return

    print(
        f"\nReport for {report['year']}-"
        f"{report['month']:02d}"
    )
    print("-" * 35)
    print(f"Transactions:    {report['transaction_count']}")
    print(f"Total income:    ${report['total_income']:.2f}")
    print(f"Total expenses:  ${report['total_expenses']:.2f}")
    print(f"Monthly balance: ${report['balance']:.2f}")

    print("\n--- SPENDING BY CATEGORY ---")

    categories = report["spending_by_category"]

    if not categories:
        print("No expenses recorded for this month.")
    else:
        for category, amount in categories.items():
            print(f"{category:<20} ${amount:.2f}")


def main():
    database.initialize_database()

    while True:
        print("\n===== PERSONAL EXPENSE TRACKER =====")
        print("1. Add income")
        print("2. Add expense")
        print("3. View transactions")
        print("4. View financial summary")
        print("5. Exit")
        print("6. Edit transaction")
        print("7. Delete transaction")
        print("8. Filter transactions by date and category")
        print("9. Export transactions to CSV")
        print("10. Monthly spending report")

        choice = input("Choose an option (1-10): ").strip()

        if choice in ("1", "2"):
            transaction_type = (
                "income" if choice == "1" else "expense"
            )

            category = input("Enter category: ").strip()
            description = input("Enter description: ").strip()

            try:
                amount = float(input("Enter amount: $"))

                add_transaction(
                    transaction_type,
                    category,
                    description,
                    amount,
                )
                print("Transaction saved successfully!")

            except ValueError as error:
                print(f"Invalid input: {error}")

        elif choice == "3":
            display_transactions()

        elif choice == "4":
            display_summary()

        elif choice == "5":
            print("Goodbye!")
            break

        elif choice == "6":
            edit_transaction()

        elif choice == "7":
            remove_transaction()

        elif choice == "8":
            filter_transactions()

        elif choice == "9":
            export_csv_report()

        elif choice == "10":
            display_monthly_report()
        else:
            print("Invalid option. Choose from 1 to 10.")


if __name__ == "__main__":
    main()
