from datetime import date
from decimal import Decimal
from pathlib import Path
import sys

import pytest

SRC_FINANCE = Path(__file__).parents[1] / "src" / "finance"
sys.path.insert(0, str(SRC_FINANCE))

from ledger import Ledger
from transaction import Transaction


def make_transaction(transaction_type: str, amount: str) -> Transaction:
    return Transaction(
        transaction_type=transaction_type,
        amount=Decimal(amount),
        category="general",
        description="test transaction",
        transaction_date=date(2026, 7, 13),
    )


def test_new_ledger_lists_no_transactions():
    ledger = Ledger()

    assert ledger.list_transactions() == []


def test_add_transaction_stores_a_transaction():
    ledger = Ledger()
    transaction = make_transaction("income", "100.00")

    ledger.add_transaction(transaction)

    assert ledger.list_transactions() == [transaction]


def test_list_transactions_preserves_addition_order():
    ledger = Ledger()
    first = make_transaction("income", "100.00")
    second = make_transaction("expense", "25.00")

    ledger.add_transaction(first)
    ledger.add_transaction(second)

    assert ledger.list_transactions() == [first, second]


def test_list_transactions_orders_transactions_by_date_ascending():
    ledger = Ledger()
    july_thirteenth = Transaction(
        transaction_type="income",
        amount=Decimal("100.00"),
        category="general",
        description="test transaction",
        transaction_date=date(2026, 7, 13),
    )
    july_first = Transaction(
        transaction_type="expense",
        amount=Decimal("25.00"),
        category="general",
        description="test transaction",
        transaction_date=date(2026, 7, 1),
    )
    july_twelfth = Transaction(
        transaction_type="expense",
        amount=Decimal("10.00"),
        category="general",
        description="test transaction",
        transaction_date=date(2026, 7, 12),
    )

    ledger.add_transaction(july_thirteenth)
    ledger.add_transaction(july_first)
    ledger.add_transaction(july_twelfth)

    assert ledger.list_transactions() == [july_first, july_twelfth, july_thirteenth]


def test_add_transaction_rejects_a_non_transaction_value():
    ledger = Ledger()

    with pytest.raises(TypeError):
        ledger.add_transaction("not a transaction")


def test_list_transactions_returns_a_copy_of_the_internal_list():
    ledger = Ledger()
    ledger.add_transaction(make_transaction("income", "100.00"))

    listed_transactions = ledger.list_transactions()
    listed_transactions.clear()

    assert len(ledger.list_transactions()) == 1


def test_empty_ledger_has_zero_total_income():
    ledger = Ledger()

    assert ledger.total_income() == Decimal("0.00")


def test_empty_ledger_has_zero_total_expenses():
    ledger = Ledger()

    assert ledger.total_expenses() == Decimal("0.00")


def test_total_income_includes_only_income_transactions():
    ledger = Ledger()
    ledger.add_transaction(make_transaction("income", "100.00"))
    ledger.add_transaction(make_transaction("income", "25.50"))
    ledger.add_transaction(make_transaction("expense", "10.00"))

    assert ledger.total_income() == Decimal("125.50")


def test_total_expenses_includes_only_expense_transactions():
    ledger = Ledger()
    ledger.add_transaction(make_transaction("income", "100.00"))
    ledger.add_transaction(make_transaction("expense", "10.00"))
    ledger.add_transaction(make_transaction("expense", "25.50"))

    assert ledger.total_expenses() == Decimal("35.50")


def test_balance_subtracts_total_expenses_from_total_income():
    ledger = Ledger()
    ledger.add_transaction(make_transaction("income", "100.00"))
    ledger.add_transaction(make_transaction("expense", "25.50"))

    assert ledger.balance() == Decimal("74.50")
