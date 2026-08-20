import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

SRC_DIRECTORY = Path(__file__).parents[1] / "src"
sys.path.insert(0, str(SRC_DIRECTORY))

from finance.reporting import format_transaction_table
from finance.transaction import Transaction

def make_transaction(**overrides) -> Transaction:
    values = {
        "id": 1,
        "transaction_type": "income",
        "amount": Decimal("100.00"),
        "category": "salary",
        "description": "monthly salary",
        "transaction_date": date(2026, 7, 13),
    }
    values.update(overrides)
    return Transaction(**values)

def test_returns_message_for_empty_input():
    result = format_transaction_table([])

    assert result == "No transactions found."

def test_exact_format():
    transaction_list : list[Transaction] = []

    for i in range(2) :
        if i % 2 == 0 :
            transaction = make_transaction(id = 1, transaction_type = "income", category = "salary")
        else:
            transaction = make_transaction(
                id = i, transaction_type = "expense", category = "wellbeing"
            )

        transaction_list.append(transaction)

    result = format_transaction_table(transaction_list)

    head_string = (
        " ID | DATE       | TYPE    |     AMOUNT | CATEGORY     | DESCRIPTION"
    )

    string_1 = (
        "\n  1 | 2026-07-13 | income  |    €100.00 | salary       | monthly salary"
    )

    string_2 = (
        "\n  1 | 2026-07-13 | expense |    €100.00 | wellbeing    | monthly salary"
    )

    assertion_string = head_string + string_1 + string_2

    assert assertion_string == result


def test_formats_one_hundred_transactions_without_skipping_or_reordering():
    transactions = [
        make_transaction(id=transaction_id, description=f"transaction {transaction_id}")
        for transaction_id in range(1, 101)
    ]

    result = format_transaction_table(transactions)
    lines = result.splitlines()

    assert len(lines) == len(transactions) + 1

    for transaction, row in zip(transactions, lines[1:], strict=True):
        assert row.startswith(f"{transaction.id:>3} |")
        assert row.endswith(f"transaction {transaction.id}")

def test_formats_empty_description():
    transaction = make_transaction(id=1, description="")
    result = format_transaction_table([transaction])

    head_string = (
        " ID | DATE       | TYPE    |     AMOUNT | CATEGORY     | DESCRIPTION"
    )

    string_1 = (
        "\n  1 | 2026-07-13 | income  |    €100.00 | salary       | -"
    )

    assertion_string = head_string + string_1

    assert assertion_string == result