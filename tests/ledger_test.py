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


def test_list_transactions_filters_by_expense_type_in_date_order():
    ledger = Ledger()
    later_expense = Transaction(
        transaction_type="expense",
        amount=Decimal("30.00"),
        category="general",
        transaction_date=date(2026, 7, 20),
    )
    income = Transaction(
        transaction_type="income",
        amount=Decimal("100.00"),
        category="general",
        transaction_date=date(2026, 7, 10),
    )
    earlier_expense = Transaction(
        transaction_type="expense",
        amount=Decimal("10.00"),
        category="general",
        transaction_date=date(2026, 7, 5),
    )

    ledger.add_transaction(later_expense)
    ledger.add_transaction(income)
    ledger.add_transaction(earlier_expense)

    assert ledger.list_transactions(transaction_type="expense") == [earlier_expense, later_expense]


def test_list_transactions_filters_by_income_type():
    ledger = Ledger()
    expense = make_transaction("expense", "20.00")
    income = make_transaction("income", "100.00")

    ledger.add_transaction(expense)
    ledger.add_transaction(income)

    assert ledger.list_transactions(transaction_type="income") == [income]


def test_list_transactions_rejects_an_unknown_type():
    ledger = Ledger()

    with pytest.raises(ValueError):
        ledger.list_transactions(transaction_type="transfer")


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

    assert ledger.summary().income == Decimal("0.00")


def test_empty_ledger_has_zero_total_expenses():
    ledger = Ledger()

    assert ledger.summary().expenses == Decimal("0.00")


def test_total_income_includes_only_income_transactions():
    ledger = Ledger()
    ledger.add_transaction(make_transaction("income", "100.00"))
    ledger.add_transaction(make_transaction("income", "25.50"))
    ledger.add_transaction(make_transaction("expense", "10.00"))

    assert ledger.summary().income == Decimal("125.50")


def test_total_expenses_includes_only_expense_transactions():
    ledger = Ledger()
    ledger.add_transaction(make_transaction("income", "100.00"))
    ledger.add_transaction(make_transaction("expense", "10.00"))
    ledger.add_transaction(make_transaction("expense", "25.50"))

    assert ledger.summary().expenses == Decimal("35.50")


def test_balance_subtracts_total_expenses_from_total_income():
    ledger = Ledger()
    ledger.add_transaction(make_transaction("income", "100.00"))
    ledger.add_transaction(make_transaction("expense", "25.50"))

    assert ledger.summary().balance == Decimal("74.50")


def make_detailed_transaction(
    transaction_type: str,
    amount: str,
    category: str,
    transaction_date: date,
) -> Transaction:
    return Transaction(
        transaction_type=transaction_type,
        amount=Decimal(amount),
        category=category,
        description="test transaction",
        transaction_date=transaction_date,
    )


def test_list_transactions_combines_type_category_and_date_filters_with_and():
    ledger = Ledger()
    matching_expense = make_detailed_transaction(
        "expense", "12.50", "food", date(2026, 7, 12)
    )
    income_in_july = make_detailed_transaction(
        "income", "1500.00", "salary", date(2026, 7, 1)
    )
    food_in_august = make_detailed_transaction(
        "expense", "25.00", "food", date(2026, 8, 2)
    )
    transport_in_july = make_detailed_transaction(
        "expense", "30.00", "transport", date(2026, 7, 13)
    )

    for transaction in (income_in_july, food_in_august, transport_in_july, matching_expense):
        ledger.add_transaction(transaction)

    assert ledger.list_transactions(
        transaction_type="expense",
        category="food",
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 31),
    ) == [matching_expense]


def test_list_transactions_normalizes_the_category_filter():
    ledger = Ledger()
    food = make_detailed_transaction(
        "expense", "12.50", "food", date(2026, 7, 12)
    )
    transport = make_detailed_transaction(
        "expense", "30.00", "transport", date(2026, 7, 13)
    )
    ledger.add_transaction(transport)
    ledger.add_transaction(food)

    assert ledger.list_transactions(category=" Food ") == [food]


def test_list_transactions_includes_both_date_range_boundaries():
    ledger = Ledger()
    start = make_detailed_transaction(
        "expense", "10.00", "food", date(2026, 7, 1)
    )
    middle = make_detailed_transaction(
        "expense", "12.50", "food", date(2026, 7, 12)
    )
    end = make_detailed_transaction(
        "expense", "15.00", "food", date(2026, 7, 31)
    )
    outside = make_detailed_transaction(
        "expense", "20.00", "food", date(2026, 8, 1)
    )

    for transaction in (outside, end, start, middle):
        ledger.add_transaction(transaction)

    assert ledger.list_transactions(
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 31),
    ) == [start, middle, end]


def test_empty_summary_has_zero_totals_and_no_expense_categories():
    ledger = Ledger()

    summary = ledger.summary()

    assert summary.income == Decimal("0.00")
    assert summary.expenses == Decimal("0.00")
    assert summary.balance == Decimal("0.00")
    assert summary.expense_categories == []


def test_list_transactions_with_only_start_date_includes_that_date_and_later_dates():
    ledger = Ledger()
    before_start = make_detailed_transaction(
        "expense", "5.00", "food", date(2026, 6, 30)
    )
    start = make_detailed_transaction(
        "expense", "10.00", "food", date(2026, 7, 1)
    )
    later = make_detailed_transaction(
        "income", "100.00", "salary", date(2026, 7, 20)
    )

    for transaction in (later, before_start, start):
        ledger.add_transaction(transaction)

    assert ledger.list_transactions(start_date=date(2026, 7, 1)) == [start, later]


def test_list_transactions_with_only_end_date_includes_that_date_and_earlier_dates():
    ledger = Ledger()
    earlier = make_detailed_transaction(
        "expense", "5.00", "food", date(2026, 6, 30)
    )
    end = make_detailed_transaction(
        "expense", "10.00", "food", date(2026, 7, 31)
    )
    after_end = make_detailed_transaction(
        "income", "100.00", "salary", date(2026, 8, 1)
    )

    for transaction in (after_end, end, earlier):
        ledger.add_transaction(transaction)

    assert ledger.list_transactions(end_date=date(2026, 7, 31)) == [earlier, end]




def test_list_transactions_rejects_a_reversed_date_range():
    ledger = Ledger()

    with pytest.raises(ValueError, match="start_date cannot be after end_date"):
        ledger.list_transactions(
            start_date=date(2026, 7, 31),
            end_date=date(2026, 7, 1),
        )


def test_ledger_summary_on_an_empty_ledger_returns_a_finished_summary_value():
    ledger = Ledger()

    summary = ledger.summary()

    assert summary.income == Decimal("0.00")
    assert summary.expenses == Decimal("0.00")
    assert summary.balance == Decimal("0.00")
    assert summary.expense_categories == []


def test_monthly_summary_includes_only_the_requested_year_and_month():
    ledger = Ledger()
    july_income = make_detailed_transaction(
        "income", "1500.00", "salary", date(2026, 7, 1)
    )
    july_expense = make_detailed_transaction(
        "expense", "12.50", "food", date(2026, 7, 12)
    )
    august_expense = make_detailed_transaction(
        "expense", "40.00", "food", date(2026, 8, 2)
    )
    previous_year_july_expense = make_detailed_transaction(
        "expense", "50.00", "food", date(2025, 7, 12)
    )

    for transaction in (
        july_income,
        july_expense,
        august_expense,
        previous_year_july_expense,
    ):
        ledger.add_transaction(transaction)

    summary = ledger.summary(month="2026-07")

    assert summary.income == Decimal("1500.00")
    assert summary.expenses == Decimal("12.50")
    assert summary.balance == Decimal("1487.50")


@pytest.mark.parametrize("month", ["2026-7", "2026-00", "2026-13", "hello"])
def test_summary_rejects_an_invalid_month_format(month):
    ledger = Ledger()

    with pytest.raises(ValueError, match="Month must be in YYYY-MM format"):
        ledger.summary(month=month)


def test_summary_groups_expenses_and_orders_categories_by_total_then_name():
    ledger = Ledger()
    transport = make_detailed_transaction(
        "expense", "30.00", "transport", date(2026, 7, 1)
    )
    food_first = make_detailed_transaction(
        "expense", "12.50", "food", date(2026, 7, 2)
    )
    food_second = make_detailed_transaction(
        "expense", "7.50", "food", date(2026, 7, 3)
    )
    utilities = make_detailed_transaction(
        "expense", "20.00", "utilities", date(2026, 7, 4)
    )
    salary = make_detailed_transaction(
        "income", "100.00", "salary", date(2026, 7, 5)
    )

    for transaction in (salary, food_first, utilities, transport, food_second):
        ledger.add_transaction(transaction)

    assert ledger.summary().expense_categories == [
        ("transport", Decimal("30.00")),
        ("food", Decimal("20.00")),
        ("utilities", Decimal("20.00")),
    ]


def test_filtered_listing_does_not_change_the_transactions_stored_in_the_ledger():
    ledger = Ledger()
    food = make_detailed_transaction(
        "expense", "12.50", "food", date(2026, 7, 1)
    )
    transport = make_detailed_transaction(
        "expense", "30.00", "transport", date(2026, 7, 2)
    )
    salary = make_detailed_transaction(
        "income", "1500.00", "salary", date(2026, 7, 3)
    )

    for transaction in (food, transport, salary):
        ledger.add_transaction(transaction)

    assert ledger.list_transactions(category="food") == [food]
    assert ledger.list_transactions() == [food, transport, salary]


def test_summary_without_a_month_includes_transactions_from_every_month():
    ledger = Ledger()
    june_income = make_detailed_transaction(
        "income", "100.00", "salary", date(2026, 6, 30)
    )
    august_expense = make_detailed_transaction(
        "expense", "25.00", "food", date(2026, 8, 1)
    )

    ledger.add_transaction(june_income)
    ledger.add_transaction(august_expense)

    summary = ledger.summary()

    assert summary.income == Decimal("100.00")
    assert summary.expenses == Decimal("25.00")
    assert summary.balance == Decimal("75.00")
