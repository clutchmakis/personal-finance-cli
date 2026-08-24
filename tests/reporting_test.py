import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

SRC_DIRECTORY = Path(__file__).parents[1] / "src"
sys.path.insert(0, str(SRC_DIRECTORY))

from finance.ledger import Summary
from finance.reporting import format_summary_table, format_transaction_table
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


def test_formats_empty_all_time_summary():
    summary = Summary(
        income=Decimal("0.00"),
        expenses=Decimal("0.00"),
        balance=Decimal("0.00"),
        expense_categories=[],
    )

    result = format_summary_table(summary)

    assert result == (
        "All time\n"
        "Income:   €0.00\n"
        "Expenses: €0.00\n"
        "Balance:  €0.00\n"
        "\n"
        "Expenses by category:\n"
        "No expense categories."
    )


def test_formats_populated_all_time_summary():
    summary = Summary(
        income=Decimal("1500"),
        expenses=Decimal("12.5"),
        balance=Decimal("1487.5"),
        expense_categories=[("food", Decimal("12.5"))],
    )

    result = format_summary_table(summary)

    assert result == (
        "All time\n"
        "Income:   €1500.00\n"
        "Expenses: €12.50\n"
        "Balance:  €1487.50\n"
        "\n"
        "Expenses by category:\n"
        "- food: €12.50"
    )


def test_formats_monthly_summary():
    summary = Summary(
        income=Decimal("1500.00"),
        expenses=Decimal("12.50"),
        balance=Decimal("1487.50"),
        expense_categories=[("food", Decimal("12.50"))],
    )

    result = format_summary_table(summary, month="2026-07")

    assert result == (
        "Month: 2026-07\n"
        "Income:   €1500.00\n"
        "Expenses: €12.50\n"
        "Balance:  €1487.50\n"
        "\n"
        "Expenses by category:\n"
        "- food: €12.50"
    )


def test_summary_formatter_preserves_expense_category_order():
    summary = Summary(
        income=Decimal("100.00"),
        expenses=Decimal("30.00"),
        balance=Decimal("70.00"),
        expense_categories=[
            ("food", Decimal("10.00")),
            ("travel", Decimal("20.00")),
        ],
    )

    result = format_summary_table(summary)

    assert result.index("- food: €10.00") < result.index("- travel: €20.00")