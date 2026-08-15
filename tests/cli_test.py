import os
from datetime import date
from decimal import Decimal
from pathlib import Path
import subprocess
import sys

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
