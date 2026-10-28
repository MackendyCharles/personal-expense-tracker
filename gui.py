
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

import database
import reports
import monthly_reports


class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker")
        self.root.geometry("1100x700")
        self.root.minsize(850, 550)

        self.selected_id = None

        database.initialize_database()
        self._configure_style()
        self._build_interface()
        self.refresh_transactions()

    def _configure_style(self):
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("Title.TLabel", font=("Arial", 20, "bold"))
        style.configure("Metric.TLabel", font=("Arial", 12, "bold"))
        style.configure("Treeview", rowheight=28)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    def _build_interface(self):
        # Header
        header = ttk.Frame(self.root, padding=15)
        header.pack(fill="x")

        ttk.Label(
            header,
            text="Personal Expense Tracker",
            style="Title.TLabel",
        ).pack(side="left")

        ttk.Button(
            header, text="Monthly Report", command=self.show_monthly_report
        ).pack(side="right", padx=5)

        ttk.Button(
            header, text="Export CSV", command=self.export_csv
        ).pack(side="right", padx=5)

        # Financial summary
        summary = ttk.Frame(self.root, padding=(15, 0, 15, 12))
        summary.pack(fill="x")

        self.income_label = ttk.Label(summary, style="Metric.TLabel")
        self.expense_label = ttk.Label(summary, style="Metric.TLabel")
        self.balance_label = ttk.Label(summary, style="Metric.TLabel")

        self.income_label.pack(side="left", padx=(0, 30))
        self.expense_label.pack(side="left", padx=(0, 30))
        self.balance_label.pack(side="left")

        # Filters
        filters = ttk.LabelFrame(
            self.root, text="Filter transactions", padding=10
        )
        filters.pack(fill="x", padx=15, pady=(0, 10))

        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()
        self.category_var = tk.StringVar()

        ttk.Label(filters, text="Start date").grid(
            row=0, column=0, padx=5, pady=4
        )
        ttk.Entry(filters, textvariable=self.start_var, width=14).grid(
            row=0, column=1, padx=5, pady=4
        )

        ttk.Label(filters, text="End date").grid(
            row=0, column=2, padx=5, pady=4
        )
        ttk.Entry(filters, textvariable=self.end_var, width=14).grid(
            row=0, column=3, padx=5, pady=4
        )

        ttk.Label(filters, text="Category").grid(
            row=0, column=4, padx=5, pady=4
        )
        ttk.Entry(filters, textvariable=self.category_var, width=18).grid(
            row=0, column=5, padx=5, pady=4
        )

        ttk.Button(
            filters, text="Apply", command=self.apply_filters
        ).grid(row=0, column=6, padx=5)

        ttk.Button(
            filters, text="Clear", command=self.clear_filters
        ).grid(row=0, column=7, padx=5)

        # Transaction table
        table_frame = ttk.Frame(self.root, padding=(15, 0, 15, 10))
        table_frame.pack(fill="both", expand=True)

        columns = (
            "id", "date", "type", "category", "description", "amount"
        )

        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            selectmode="browse",
        )

        headings = {
            "id": "ID",
            "date": "Date",
            "type": "Type",
            "category": "Category",
            "description": "Description",
            "amount": "Amount",
        }

        widths = {
            "id": 55,
            "date": 110,
            "type": 100,
            "category": 140,
            "description": 350,
            "amount": 110,
        }

        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(
                column, width=widths[column],
                anchor="w" if column == "description" else "center",
            )

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Actions
        actions = ttk.Frame(self.root, padding=(15, 0, 15, 15))
        actions.pack(fill="x")

        ttk.Button(
            actions, text="Add Transaction", command=self.add_transaction
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            actions, text="Edit Selected", command=self.edit_transaction
        ).pack(side="left", padx=8)

        ttk.Button(
            actions, text="Delete Selected", command=self.delete_transaction
        ).pack(side="left", padx=8)

        ttk.Button(
            actions, text="Refresh", command=self.refresh_transactions
        ).pack(side="right")

    def refresh_transactions(self, transactions=None):
        if transactions is None:
            transactions = database.get_all_transactions()

        self.tree.delete(*self.tree.get_children())

        for transaction in transactions:
            self.tree.insert(
                "",
                "end",
                values=(
                    transaction["id"],
                    transaction["date"],
                    transaction["type"].upper(),
                    transaction["category"],
                    transaction["description"],
                    f'${transaction["amount"]:.2f}',
                ),
            )

        all_transactions = database.get_all_transactions()
        income = sum(
            t["amount"] for t in all_transactions
            if t["type"] == "income"
        )
        expenses = sum(
            t["amount"] for t in all_transactions
            if t["type"] == "expense"
        )

        self.income_label.config(text=f"Income: ${income:.2f}")
        self.expense_label.config(text=f"Expenses: ${expenses:.2f}")
        self.balance_label.config(text=f"Balance: ${income - expenses:.2f}")

    def apply_filters(self):
        start = self.start_var.get().strip()
        end = self.end_var.get().strip()
        category = self.category_var.get().strip()

        try:
            if start:
                date.fromisoformat(start)
            if end:
                date.fromisoformat(end)

            if start and end and start > end:
                raise ValueError("Start date must not be after end date.")

            transactions = database.get_filtered_transactions(
                start_date=start or None,
                end_date=end or None,
                category=category or None,
            )
            self.refresh_transactions(transactions)

        except ValueError as error:
            messagebox.showerror("Invalid filter", str(error))

    def clear_filters(self):
        self.start_var.set("")
        self.end_var.set("")
        self.category_var.set("")
        self.refresh_transactions()

    def _selected_transaction(self):
        selection = self.tree.selection()

        if not selection:
            messagebox.showwarning(
                "No selection", "Please select a transaction first."
            )
            return None

        values = self.tree.item(selection[0], "values")
        return database.get_transaction_by_id(int(values[0]))

    def add_transaction(self):
        self._transaction_form()

    def edit_transaction(self):
        transaction = self._selected_transaction()
        if transaction:
            self._transaction_form(transaction)

    def _transaction_form(self, transaction=None):
        editing = transaction is not None

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Transaction" if editing else "Add Transaction")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)

        type_var = tk.StringVar(
            value=transaction["type"] if editing else "expense"
        )
        category_var = tk.StringVar(
            value=transaction["category"] if editing else ""
        )
        description_var = tk.StringVar(
            value=transaction["description"] if editing else ""
        )
        amount_var = tk.StringVar(
            value=str(transaction["amount"]) if editing else ""
        )

        fields = [
            ("Type", type_var),
            ("Category", category_var),
            ("Description", description_var),
            ("Amount", amount_var),
        ]

        for row, (label, variable) in enumerate(fields):
            ttk.Label(frame, text=label).grid(
                row=row, column=0, sticky="w", padx=5, pady=7
            )

            if label == "Type":
                widget = ttk.Combobox(
                    frame, textvariable=variable,
                    values=("income", "expense"),
                    state="readonly", width=27,
                )
            else:
                widget = ttk.Entry(
                    frame, textvariable=variable, width=30
                )

            widget.grid(row=row, column=1, padx=5, pady=7)

        if editing:
            ttk.Label(
                frame,
                text=f"Transaction date: {transaction['date']} (unchanged)",
            ).grid(row=4, column=0, columnspan=2, sticky="w", pady=5)

        def save():
            transaction_type = type_var.get().strip().lower()
            category = category_var.get().strip()
            description = description_var.get().strip()

            try:
                amount = float(amount_var.get())

                if transaction_type not in ("income", "expense"):
                    raise ValueError("Choose income or expense.")
                if not category:
                    raise ValueError("Category is required.")
                if not description:
                    raise ValueError("Description is required.")
                if amount <= 0:
                    raise ValueError("Amount must be greater than zero.")

                if editing:
                    success = database.update_transaction(
                        transaction["id"],
                        transaction_type,
                        category,
                        description,
                        amount,
                    )
                    if not success:
                        raise ValueError("Transaction no longer exists.")
                else:
                    database.insert_transaction(
                        date.today().isoformat(),
                        transaction_type,
                        category,
                        description,
                        amount,
                    )

                dialog.destroy()
                self.refresh_transactions()

            except ValueError as error:
                messagebox.showerror(
                    "Invalid transaction", str(error), parent=dialog
                )

        buttons = ttk.Frame(frame)
        buttons.grid(row=5, column=0, columnspan=2, pady=(12, 0))

        ttk.Button(buttons, text="Save", command=save).pack(
            side="left", padx=5
        )
        ttk.Button(
            buttons, text="Cancel", command=dialog.destroy
        ).pack(side="left", padx=5)

    def delete_transaction(self):
        transaction = self._selected_transaction()
        if not transaction:
            return

        confirm = messagebox.askyesno(
            "Confirm deletion",
            f'Delete "{transaction["description"]}" '
            f'(${transaction["amount"]:.2f})?',
            parent=self.root,
        )

        if confirm:
            if database.delete_transaction(transaction["id"]):
                self.refresh_transactions()
            else:
                messagebox.showerror(
                    "Error", "Transaction could not be deleted."
                )

    def export_csv(self):
        start = self.start_var.get().strip()
        end = self.end_var.get().strip()
        category = self.category_var.get().strip()

        try:
            if start:
                date.fromisoformat(start)
            if end:
                date.fromisoformat(end)
            if start and end and start > end:
                raise ValueError("Start date must not be after end date.")

            filepath, count = reports.export_transactions_to_csv(
                start_date=start or None,
                end_date=end or None,
                category=category or None,
            )

            messagebox.showinfo(
                "CSV Export",
                f"Exported {count} transaction(s).\n\n"
                f"File: {filepath.resolve()}",
            )

        except (ValueError, OSError) as error:
            messagebox.showerror("Export failed", str(error))

    def show_monthly_report(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Monthly Spending Report")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)

        year_var = tk.StringVar(value=str(date.today().year))
        month_var = tk.StringVar(value=str(date.today().month))

        ttk.Label(frame, text="Year").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(frame, textvariable=year_var, width=10).grid(
            row=0, column=1, padx=5, pady=5
        )

        ttk.Label(frame, text="Month (1-12)").grid(
            row=0, column=2, padx=5, pady=5
        )
        ttk.Entry(frame, textvariable=month_var, width=8).grid(
            row=0, column=3, padx=5, pady=5
        )

        result = ttk.Label(
            frame, text="Choose a month and click Generate.",
            justify="left",
        )
        result.grid(row=2, column=0, columnspan=4, sticky="w", pady=15)

        def generate():
            try:
                report = monthly_reports.generate_monthly_report(
                    int(year_var.get()), int(month_var.get())
                )

                lines = [
                    f"Report: {report['year']}-{report['month']:02d}",
                    f"Transactions: {report['transaction_count']}",
                    f"Total income: ${report['total_income']:.2f}",
                    f"Total expenses: ${report['total_expenses']:.2f}",
                    f"Balance: ${report['balance']:.2f}",
                    "",
                    "Spending by category:",
                ]

                if report["spending_by_category"]:
                    for category, amount in (
                        report["spending_by_category"].items()
                    ):
                        lines.append(f"  {category}: ${amount:.2f}")
                else:
                    lines.append("  No expenses for this month.")

                result.config(text="\n".join(lines))

            except ValueError as error:
                messagebox.showerror(
                    "Invalid month", str(error), parent=dialog
                )

        ttk.Button(
            frame, text="Generate", command=generate
        ).grid(row=1, column=0, columnspan=4, pady=5)


def main():
    root = tk.Tk()
    ExpenseTrackerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
