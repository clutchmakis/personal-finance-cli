"""Format finance domain values for terminal presentation."""

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
