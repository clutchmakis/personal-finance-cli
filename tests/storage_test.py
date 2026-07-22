from datetime import date
from decimal import Decimal
from pathlib import Path
import sys

SRC_FINANCE = Path(__file__).parents[1] / "src" / "finance"
sys.path.insert(0, str(SRC_FINANCE))

from storage import SQLiteStorage
from transaction import Transaction


def make_transaction(**overrides) -> Transaction:
    values = {
        "transaction_type": "expense",
        "amount": Decimal("12.50"),
        "category": "food",
        "description": "Lunch with colleagues",
        "transaction_date": date(2026, 7, 12),
    }
    values.update(overrides)
    return Transaction(**values)


def test_new_storage_lists_no_transactions(tmp_path):
    storage = SQLiteStorage(tmp_path / "finance.db")

    assert storage.list_transactions() == []


def test_save_returns_a_new_transaction_with_a_positive_database_id(tmp_path):
    storage = SQLiteStorage(tmp_path / "finance.db")
    transaction = make_transaction()

    saved = storage.save(transaction)

    assert transaction.id is None
    assert isinstance(saved.id, int)
    assert saved.id > 0
    assert saved.transaction_type == transaction.transaction_type
    assert saved.amount == transaction.amount
    assert saved.category == transaction.category
    assert saved.description == transaction.description
    assert saved.transaction_date == transaction.transaction_date


def test_saved_transaction_round_trips_after_storage_is_reopened(tmp_path):
    database_path = tmp_path / "finance.db"
    saved = SQLiteStorage(database_path).save(make_transaction())

    loaded = SQLiteStorage(database_path).list_transactions()

    assert loaded == [saved]


def test_storage_round_trips_exact_cents_and_dates(tmp_path):
    storage = SQLiteStorage(tmp_path / "finance.db")
    transaction = make_transaction(amount=Decimal("12.50"), transaction_date=date(2026, 7, 1))

    saved = storage.save(transaction)

    assert storage.list_transactions() == [saved]
    assert storage.list_transactions()[0].amount == Decimal("12.50")
    assert storage.list_transactions()[0].transaction_date == date(2026, 7, 1)


def test_storage_filters_with_and_and_orders_by_date_then_id(tmp_path):
    storage = SQLiteStorage(tmp_path / "finance.db")
    matching_first = storage.save(
        make_transaction(transaction_date=date(2026, 7, 12))
    )
    storage.save(make_transaction(transaction_type="income", category="salary"))
    storage.save(make_transaction(category="transport"))
    storage.save(make_transaction(transaction_date=date(2026, 8, 1)))
    matching_second = storage.save(
        make_transaction(amount=Decimal("5.00"), transaction_date=date(2026, 7, 12))
    )

    assert storage.list_transactions(
        transaction_type="expense",
        category=" Food ",
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 31),
    ) == [matching_first, matching_second]
