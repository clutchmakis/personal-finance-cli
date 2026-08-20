import os
import subprocess
import sys
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIRECTORY))

from finance.storage import SQLiteStorage


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
