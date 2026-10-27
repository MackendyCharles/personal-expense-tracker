import csv
from datetime import datetime
from pathlib import Path

import database


REPORTS_DIR = Path(__file__).with_name("reports")


def _safe_spreadsheet_text(value):
    """Reduce formula-injection risk when opening CSV files in spreadsheets."""
    text = str(value)

    if text.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + text

    return text


def export_transactions_to_csv(
    start_date=None,
    end_date=None,
    category=None,
    filename=None,
):
    """Export matching transactions to a CSV file."""

    transactions = database.get_filtered_transactions(
        start_date=start_date,
        end_date=end_date,
        category=category,
    )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transactions_{timestamp}.csv"

    output_path = Path(filename)

    # Keep relative filenames inside the reports directory.
    if not output_path.is_absolute():
        output_path = REPORTS_DIR / output_path

    if output_path.suffix.lower() != ".csv":
        output_path = output_path.with_suffix(".csv")

    fieldnames = [
        "id",
        "date",
        "type",
        "category",
        "description",
        "amount",
    ]

    with output_path.open(
        "w", newline="", encoding="utf-8-sig"
    ) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for transaction in transactions:
            row = transaction.copy()
            row["category"] = _safe_spreadsheet_text(row["category"])
            row["description"] = _safe_spreadsheet_text(
                row["description"]
            )
            writer.writerow(row)

    return output_path, len(transactions)
