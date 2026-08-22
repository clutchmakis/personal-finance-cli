import os
import sys
import subprocess
from pathlib import Path
from decimal import Decimal
from datetime import UTC, date

PROJECT_ROOT = Path(__file__).parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIRECTORY))

from finance.storage import SQLiteStorage
from finance.transaction import Transaction



def run_finance(*arguments: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    existing_python_path = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = str(SRC_DIRECTORY) + (
        os.pathsep + existing_python_path if existing_python_path else ""
    )

    return subprocess.run(
        [sys.executable, "-m", "finance", *arguments],
        cwd=PROJECT_ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check = False,
    )


def test_add_command_saves_a_transaction_and_prints_a_success_message(tmp_path):
    database_path = tmp_path / "finance.db"

    result = run_finance(
        "--database",
        str(database_path),
        "add",
        "income",
        "1500.00",
        " Salary ",
        " July salary ",
        "--date",
        "2026-07-01",
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == "Added income #1: €1500.00 in salary on 2026-07-01.\n"
    saved_transactions = SQLiteStorage(database_path).list_transactions()
    assert [
        (
            transaction.id,
            transaction.transaction_type,
            transaction.amount,
            transaction.category,
            transaction.description,
            transaction.transaction_date,
        )
        for transaction in saved_transactions
    ] == [
        (
            1,
            "income",
            Decimal("1500.00"),
            "salary",
            "July salary",
            date(2026, 7, 1),
        )
    ]


def test_add_command_rejects_invalid_amount_without_traceback_or_saving(tmp_path):
    database_path = tmp_path / "finance.db"

    result = run_finance(
        "--database",
        str(database_path),
        "add",
        "income",
        "not-a-number",
        "salary",
    )

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert "amount must be a valid decimal number" in result.stderr.lower()
    assert SQLiteStorage(database_path).list_transactions() == []

def test_add_command_rejects_an_invalid_transaction_type(tmp_path):
    database_path = tmp_path / "finance.db"

    result = run_finance(
        "--database",
        str(database_path),
        "add",
        "transfer",
        "10",
        "food",
    )

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert "not expense or income" in result.stderr.lower()
    assert SQLiteStorage(database_path).list_transactions() == []


def test_add_command_rejects_an_impossible_date(tmp_path):
    database_path = tmp_path / "finance.db"

    result = run_finance(
        "--database",
        str(database_path),
        "add",
        "income",
        "10",
        "food",
        "--date",
        "2026-02-30",
    )

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert "date must use yyyy-mm-dd format" in result.stderr.lower()
    assert SQLiteStorage(database_path).list_transactions() == []


def test_add_command_rejects_zero_amount(tmp_path):
    database_path = tmp_path / "finance.db"

    result = run_finance(
        "--database",
        str(database_path),
        "add",
        "expense",
        "0",
        "food",
    )

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert SQLiteStorage(database_path).list_transactions() == []


def test_add_command_rejects_negative_amount(tmp_path):
    database_path = tmp_path / "finance.db"

    result = run_finance(
        "--database",
        str(database_path),
        "add",
        "expense",
        "-100",
        "food",
    )

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert SQLiteStorage(database_path).list_transactions() == []


def test_add_command_rejects_amount_with_more_than_two_decimals(tmp_path):
    database_path = tmp_path / "finance.db"

    result = run_finance(
        "--database",
        str(database_path),
        "add",
        "expense",
        "30.123",
        "food",
    )

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert SQLiteStorage(database_path).list_transactions() == []


def test_add_command_rejects_a_whitespace_only_category(tmp_path):
    database_path = tmp_path / "finance.db"

    result = run_finance(
        "--database",
        str(database_path),
        "add",
        "expense",
        "30.16",
        "   ",
    )

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert "category can not be empty" in result.stderr.lower()
    assert SQLiteStorage(database_path).list_transactions() == []


def test_add_command_defaults_an_omitted_description_to_an_empty_string(tmp_path):
    database_path = tmp_path / "finance.db"

    result = run_finance(
        "--database",
        str(database_path),
        "add",
        "income",
        "83",
        "food",
        "--date",
        "2026-07-01",
    )

    assert result.returncode == 0
    saved_transactions = SQLiteStorage(database_path).list_transactions()
    assert len(saved_transactions) == 1
    assert saved_transactions[0].description == ""


def test_add_command_defaults_an_omitted_date_to_today(tmp_path):
    database_path = tmp_path / "finance.db"
    today = date.today()

    result = run_finance(
        "--database",
        str(database_path),
        "add",
        "income",
        "83",
        "food",
        "Restaurant to eat",
    )

    assert result.returncode == 0
    saved_transactions = SQLiteStorage(database_path).list_transactions()
    assert len(saved_transactions) == 1
    assert saved_transactions[0].transaction_date == today


def test_add_command_prints_a_whole_number_amount_with_two_decimal_places(tmp_path):
    database_path = tmp_path / "finance.db"

    result = run_finance(
        "--database",
        str(database_path),
        "add",
        "income",
        "83",
        "food",
        "--date",
        "2026-07-01",
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == "Added income #1: €83.00 in food on 2026-07-01.\n"


def save_list_transaction(
    storage: SQLiteStorage,
    *,
    transaction_type: str = "expense",
    category: str = "food",
    transaction_date: date = date(2026, 7, 15),
    description: str,
) -> Transaction:
    return storage.save(
        Transaction(
            transaction_type=transaction_type,
            amount=Decimal("10.00"),
            category=category,
            description=description,
            transaction_date=transaction_date,
        )
    )


def test_list_command_prints_message_for_empty_database(tmp_path):
    database_path = tmp_path / "finance.db"

    result = run_finance(
        "--database",
        str(database_path),
        "list"
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == "No transactions found.\n"

def test_list_command_prints_two_transactions_in_chronological_order(tmp_path):
    database_path = tmp_path / "finance.db"
    storage = SQLiteStorage(database_path)

    later_transaction = Transaction(
        transaction_type="income",
        amount=Decimal("6133.43"),
        category="salary",
        description="monthly salary",
        transaction_date=date(2026, 7, 10),
    )
    earlier_transaction = Transaction(
        transaction_type="income",
        amount=Decimal("69.3"),
        category="salary",
        description="monthly salary",
        transaction_date=date(2026, 7, 2),
    )

    storage.save(later_transaction)
    storage.save(earlier_transaction)

    result = run_finance(
        "--database",
        str(database_path),
        "list",
    )

    assert result.returncode == 0
    assert result.stderr == ""

    lines = result.stdout.splitlines()

    assert lines[0] == (
        " ID | DATE       | TYPE    |     AMOUNT | CATEGORY     | DESCRIPTION"
    )
    assert lines[1].startswith("  2 | 2026-07-02 |")
    assert "€69.30" in lines[1]
    assert lines[2].startswith("  1 | 2026-07-10 |")
    assert "€6133.43" in lines[2]


def test_list_command_filters_by_transaction_type(tmp_path):
    database_path = tmp_path / "finance.db"
    storage = SQLiteStorage(database_path)
    save_list_transaction(storage, description="matching expense")
    save_list_transaction(
        storage,
        transaction_type="income",
        category="salary",
        description="excluded income",
    )

    result = run_finance(
        "--database",
        str(database_path),
        "list",
        "--type",
        "expense",
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert "matching expense" in result.stdout
    assert "excluded income" not in result.stdout


def test_list_command_filters_by_normalized_category(tmp_path):
    database_path = tmp_path / "finance.db"
    storage = SQLiteStorage(database_path)
    save_list_transaction(storage, description="matching food")
    save_list_transaction(
        storage,
        category="transport",
        description="excluded transport",
    )

    result = run_finance(
        "--database",
        str(database_path),
        "list",
        "--category",
        " FOOD ",
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert "matching food" in result.stdout
    assert "excluded transport" not in result.stdout


def test_list_command_start_date_is_inclusive(tmp_path):
    database_path = tmp_path / "finance.db"
    storage = SQLiteStorage(database_path)
    save_list_transaction(
        storage,
        transaction_date=date(2026, 6, 30),
        description="excluded before start",
    )
    save_list_transaction(
        storage,
        transaction_date=date(2026, 7, 1),
        description="included on start",
    )

    result = run_finance(
        "--database",
        str(database_path),
        "list",
        "--start-date",
        "2026-07-01",
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert "included on start" in result.stdout
    assert "excluded before start" not in result.stdout


def test_list_command_end_date_is_inclusive(tmp_path):
    database_path = tmp_path / "finance.db"
    storage = SQLiteStorage(database_path)
    save_list_transaction(
        storage,
        transaction_date=date(2026, 7, 31),
        description="included on end",
    )
    save_list_transaction(
        storage,
        transaction_date=date(2026, 8, 1),
        description="excluded after end",
    )

    result = run_finance(
        "--database",
        str(database_path),
        "list",
        "--end-date",
        "2026-07-31",
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert "included on end" in result.stdout
    assert "excluded after end" not in result.stdout


def test_list_command_combines_all_filters_with_and(tmp_path):
    database_path = tmp_path / "finance.db"
    storage = SQLiteStorage(database_path)
    save_list_transaction(storage, description="only matching transaction")
    save_list_transaction(
        storage,
        transaction_type="income",
        description="excluded by type",
    )
    save_list_transaction(
        storage,
        category="transport",
        description="excluded by category",
    )
    save_list_transaction(
        storage,
        transaction_date=date(2026, 8, 1),
        description="excluded by date",
    )

    result = run_finance(
        "--database",
        str(database_path),
        "list",
        "--type",
        "expense",
        "--category",
        " FOOD ",
        "--start-date",
        "2026-07-01",
        "--end-date",
        "2026-07-31",
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert "only matching transaction" in result.stdout
    assert "excluded by type" not in result.stdout
    assert "excluded by category" not in result.stdout
    assert "excluded by date" not in result.stdout


def test_list_command_rejects_a_reversed_date_range(tmp_path):
    database_path = tmp_path / "finance.db"

    result = run_finance(
        "--database",
        str(database_path),
        "list",
        "--start-date",
        "2026-07-31",
        "--end-date",
        "2026-07-01",
    )

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert "start_date cannot be after end_date" in result.stderr


def test_list_command_rejects_an_unknown_transaction_type(tmp_path):
    database_path = tmp_path / "finance.db"

    result = run_finance(
        "--database",
        str(database_path),
        "list",
        "--type",
        "transfer",
    )

    assert result.returncode != 0
    assert result.stdout == ""
    assert "Traceback" not in result.stderr
    assert "transaction type must be either expense or income" in result.stderr.lower()


def test_list_command_rejects_an_invalid_start_date_without_a_traceback(tmp_path):
    database_path = tmp_path / "finance.db"

    result = run_finance(
        "--database",
        str(database_path),
        "list",
        "--start-date",
        "2026-02-30",
    )

    assert result.returncode != 0
    assert result.stdout == ""
    assert "Traceback" not in result.stderr
    assert "error:" in result.stderr.lower()


def test_list_command_prints_empty_message_when_filters_match_nothing(tmp_path):
    database_path = tmp_path / "finance.db"
    storage = SQLiteStorage(database_path)
    save_list_transaction(storage, description="july expense")

    result = run_finance(
        "--database",
        str(database_path),
        "list",
        "--start-date",
        "2026-08-01",
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == "No transactions found.\n"
