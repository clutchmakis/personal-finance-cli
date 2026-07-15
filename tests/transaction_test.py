from datetime import date
from decimal import Decimal
from pathlib import Path
import sys

import pytest

SRC_FINANCE = Path(__file__).parents[1] / "src" / "finance"
sys.path.insert(0, str(SRC_FINANCE))

from transaction import Transaction


def make_transaction(**overrides) -> Transaction:
    values = {
        "transaction_type": "income",
        "amount": Decimal("100.00"),
        "category": "salary",
        "description": "monthly salary",
        "transaction_date": date(2026, 7, 13),
    }
    values.update(overrides)
    return Transaction(**values)


def test_transaction_normalizes_transaction_type_and_category():
    transaction = make_transaction(
        transaction_type="  INCOME  ", category="  Salary  "
    )

    assert transaction.transaction_type == "income"
    assert transaction.category == "salary"


def test_transaction_rejects_an_unknown_transaction_type():
    with pytest.raises(ValueError):
        make_transaction(transaction_type="transfer")

def test_transaction_defaults_a_missing_description_to_empty_string():
    transaction = Transaction(
        transaction_type="income",
        amount=Decimal("100.00"),
        category="salary",
        transaction_date=date(2026, 7, 13),
    )

    assert transaction.description == ""

def test_transaction_rejects_a_non_string_transaction_type():
    with pytest.raises(TypeError):
        make_transaction(transaction_type=1)


def test_transaction_rejects_a_zero_amount():
    with pytest.raises(ValueError):
        make_transaction(amount=Decimal("0.00"))


def test_transaction_rejects_a_negative_amount():
    with pytest.raises(ValueError):
        make_transaction(amount=Decimal("-1.00"))


def test_transaction_rejects_a_non_decimal_amount():
    with pytest.raises(TypeError):
        make_transaction(amount=100)


def test_transaction_rejects_an_amount_with_more_than_two_decimal_places():
    with pytest.raises(ValueError):
        make_transaction(amount=Decimal("10.001"))


def test_transaction_rejects_an_empty_category():
    with pytest.raises(ValueError):
        make_transaction(category="   ")


def test_transaction_rejects_a_non_string_category():
    with pytest.raises(TypeError):
        make_transaction(category=1)


def test_transaction_rejects_a_non_date_transaction_date():
    with pytest.raises(TypeError):
        make_transaction(transaction_date="2026-07-13")
