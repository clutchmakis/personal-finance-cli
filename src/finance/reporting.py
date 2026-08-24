"""Format finance domain values for terminal presentation."""

from decimal import Decimal

from .ledger import Summary
from .transaction import Transaction


def format_transaction_table(transaction_list: list[Transaction]) -> str:
    """Return a transaction table while preserving the supplied row order."""
    if not transaction_list:
        return "No transactions found."

    header = (
        f'{"ID":>3} | {"DATE":<10} | {"TYPE":<7} | '
        f'{"AMOUNT":>10} | {"CATEGORY":<12} | DESCRIPTION'
    )
    rows = [header]

    for transaction in transaction_list:
        amount_string = f"€{transaction.amount:.2f}"
        date_string = transaction.transaction_date.isoformat()
        description = transaction.description or "-"

        row = (
            f"{transaction.id:>3} | {date_string:<10} | "
            f"{transaction.transaction_type:<7} | {amount_string:>10} | "
            f"{transaction.category:<12} | {description}"
        )
        rows.append(row)

    return "\n".join(rows)


def format_amount(amount: Decimal) -> str:
    # Convert it to a string with .00
    correct_amount = f"€{format(amount, ".2f")}"
    return correct_amount



def format_expense_categories(
    categories: list[tuple[str, Decimal]],
) -> str:
    """Return expense-category rows while preserving their order."""

    if not categories:
        expenses_categories = "No expense categories."
    else:
        category_lines = []

        #  Format categories in the order supplied by the ledger.
        for category, amount in categories:
            category_lines.append(f"- {category}: {format_amount(amount)}")

        expenses_categories = "\n".join(category_lines)

    return expenses_categories


def format_summary_table(summary: Summary, month: str | None = None) -> str:
    "Return formatted summary text"

    income = format_amount(summary.income)
    expenses = format_amount(summary.expenses)
    balance = format_amount(summary.balance)
    expenses_categories = format_expense_categories(summary.expense_categories)

    if month is None :
        string = ('All time\n' +
                f'Income:   {income}\n' +
                f'Expenses: {expenses}\n' +
                f'Balance:  {balance}\n' +
                '\n' +
                'Expenses by category:\n'+
                f'{expenses_categories}'
        )
        return string
    else:
        string = (f'Month: {month}\n' +
                f'Income:   {income}\n' +
                f'Expenses: {expenses}\n' +
                f'Balance:  {balance}\n' +
                '\n' +
                'Expenses by category:\n' +
                f'{expenses_categories}'
        )
        return string