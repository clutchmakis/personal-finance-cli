# Personal Finance CLI — Requirements Guide

**Goal:** Build a small terminal program for one person to record income and expenses, save them locally, inspect them, summarize them, and export them.

**Stack:** Python 3.11+, standard library only (`decimal`, `datetime`, `argparse`, `sqlite3`, `csv`) plus `pytest`. This is deliberately **not** a web app. Do not add FastAPI, SQLAlchemy, Docker, user accounts, authentication, budgets, or a frontend.

---

## 1. What the finished application does

A user runs commands such as:

```text
finance add expense 12.50 food "Lunch with colleagues" --date 2026-07-12
finance add income 1500.00 salary "July salary" --date 2026-07-01
finance list
finance list --category food --from 2026-07-01 --to 2026-07-31
finance summary --month 2026-07
finance export --month 2026-07 --output july-2026.csv
```

Expected summary for the first two records:

```text
Month: 2026-07
Income:   €1500.00
Expenses: €12.50
Balance:  €1487.50

Expenses by category:
- food: €12.50
```

The rule is:

```text
balance = total income - total expenses
```

## 2. Fixed product decisions

| Topic | Requirement |
|---|---|
| Transaction kinds | Exactly `income` and `expense`. |
| Money | Use `Decimal`, never `float`. Store in SQLite as integer cents. |
| Currency | Display euro amounts only; do not store a currency field. |
| Categories | User-entered text. Normalize with `strip().lower()`; ` Food ` becomes `food`. |
| Date | Use `datetime.date` in Python and `YYYY-MM-DD` text in SQLite. |
| ID | `None` before saving; SQLite assigns a positive integer after saving. |
| Storage | One SQLite database, default path `data/finance.db`. |
| Ordering | List records by date ascending, then ID ascending. |
| Errors | Expected invalid input must show a concise message, return non-zero, save nothing, and never show a traceback. |

## 3. Transaction rules

A transaction has these fields:

```text
id: int | None
transaction_type: str
amount: Decimal
category: str
description: str
transaction_date: date
```

Validation rules:

1. Type must be exactly `income` or `expense`.
2. Amount must be greater than zero.
3. Amount cannot have more than two decimal places: `12.50` valid, `12.999` invalid.
4. Category is trimmed, lowercased, and cannot be empty.
5. Description is optional; default is `""`; trim surrounding spaces.
6. Date must be a real calendar date.

Reject these records before any database operation:

```text
expense 0.00 food "Lunch" 2026-07-12
income -50.00 gift "Refund" 2026-07-12
transfer 20.00 food "Lunch" 2026-07-12
expense 12.999 food "Lunch" 2026-07-12
expense 12.50 "   " "Lunch" 2026-07-12
expense 12.50 food "Lunch" 2026-02-30
```

## 4. Required commands

### Add

```text
finance add TYPE AMOUNT CATEGORY [DESCRIPTION] [--date YYYY-MM-DD]
```

- Type, amount, and category are required.
- Description defaults to an empty string.
- Date defaults to the local current date if omitted.
- On success, persist the transaction and print its ID, normalized category, date, type, and two-decimal euro amount.

Example:

```text
Added expense #1: €12.50 in food on 2026-07-12.
```

### List

```text
finance list [--type income|expense] [--category CATEGORY] [--from YYYY-MM-DD] [--to YYYY-MM-DD]
```

- All filters are optional and combine with AND.
- `--from` and `--to` are inclusive.
- Reject a range where `from > to`.
- If nothing matches, print exactly `No transactions found.` and exit successfully.
- Otherwise print columns: `ID`, `DATE`, `TYPE`, `AMOUNT`, `CATEGORY`, `DESCRIPTION`.

### Summary

```text
finance summary [--month YYYY-MM]
```

- With no month: summarize everything.
- With a month: select only that calendar month; reject malformed/impossible months.
- Print income, expense, and balance to two decimal places.
- Group **expense** transactions by category only.
- Order category rows by amount descending, then category alphabetically.
- For no matching records: all totals are `€0.00` and category section says `No expense categories.`

### Export

```text
finance export --output PATH [--month YYYY-MM]
```

- `--output` is required.
- Create UTF-8 CSV with exactly this header:

```text
id,date,type,amount,category,description
```

- Amount has exactly two decimal places, no euro symbol.
- It is valid to export zero matching rows: create a header-only CSV and report success.

### Help

Use `argparse` help. `finance --help`, `finance add --help`, etc. must work. Unknown commands and missing required arguments must return non-zero with usage information.

## 5. Database specification

Every command supports this global test/development option:

```text
finance --database /path/to/test.db add expense 12.50 food
```

Default database: `data/finance.db`.

Use one table:

```sql
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('income', 'expense')),
    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
    category TEXT NOT NULL CHECK (length(category) > 0),
    description TEXT NOT NULL DEFAULT '',
    transaction_date TEXT NOT NULL
);
```

Storage rules:

- Convert validated `Decimal('12.50')` to `1250` cents before insert.
- Convert cents back to a two-decimal `Decimal` on read.
- Store dates using `date.isoformat()` and parse with `date.fromisoformat()`.
- Initialize the table automatically before the first operation.
- Use parameterized `?` SQL placeholders. Never build SQL by string interpolation.
- Keep all SQL in the storage module. The CLI and ledger never contain SQL.

## 6. Project structure and responsibilities

```text
src/finance/
  __init__.py
  __main__.py       # makes python -m finance work
  transaction.py    # Transaction and validation
  ledger.py         # add/list/filter/totals/summary rules
  storage.py        # SQLite initialization and queries
  reporting.py      # table text, summary text, CSV export
  cli.py            # argparse, calls other layers, prints results

tests/
  transaction_test.py
  ledger_test.py
  storage_test.py
  reporting_test.py
  cli_test.py
```

- `Transaction`: represents **one already-valid financial event**; no SQL, no printing.
- `Ledger`: applies finance rules to collections; no argparse, no printing.
- `Storage`: handles database conversion and queries; no terminal parsing or output formatting.
- `Reporting`: turns supplied data into text/CSV; does not query a database or calculate core rules.
- `CLI`: parses input, calls the layers, displays output, and catches expected application errors.

Use composition: the ledger receives a storage object. Do **not** make a transaction inherit from ledger/storage/CLI classes.

Suggested target interface:

```python
@dataclass(frozen=True)
class Transaction:
    transaction_type: str
    amount: Decimal
    category: str
    description: str
    transaction_date: date
    id: int | None = None

class Ledger:
    def add_transaction(self, transaction: Transaction) -> Transaction: ...
    def list_transactions(self, *, transaction_type=None, category=None,
                          start_date=None, end_date=None) -> list[Transaction]: ...
    def summary(self, month: str | None = None) -> Summary: ...
```

## 7. Build in five milestones

### Milestone 1: Transaction and in-memory ledger

Build `Transaction`, validation, in-memory `Ledger.add_transaction()`, `list_transactions()`, total income, total expenses, and balance.

**Do not build:** SQLite, CLI, CSV, or filters.

**Done when:** valid income/expense work; invalid type/amount/category/date/precision fail; totals are correct; at least 10 focused tests pass.

### Milestone 2: Filtering and summaries

Add type/category/date filters, reversed-range validation, month selection, and category expense totals.

**Done when:** filters do not mutate stored records; empty summaries are zero; only selected month appears; expense categories have required ordering; at least 16 tests pass.

### Milestone 3: SQLite persistence

Add the exact table, save/load, auto-initialization, generated ID, and conversion between `Decimal` and cents.

**Done when:** save to a temporary database, close storage, reopen it, and retrieve an identical transaction; at least 22 tests pass.

### Milestone 4: CLI

Add commands strictly in order: `add`, then `list`, then `summary`, then `export`.

**Done when:** a separate later command reads data written by `add`; invalid command input has no traceback and no write; at least 28 tests pass.

### Milestone 5: Finish properly

Add CSV, `README.md` (rename existing `READ.md`), package metadata/console script in `pyproject.toml`, setup and usage documentation.

**Done when:** a fresh environment can install it and run `finance --help`; full suite has at least 30 meaningful tests; no database/cache/environment files are staged in git.

## 8. Required tests

Use TDD for every behavior: write one failing test, run it and observe the expected failure, write minimal code, run it again, then run the full suite.

Minimum tests:

1. valid income
2. valid expense
3. zero amount rejected
4. negative amount rejected
5. unknown type rejected
6. more than two decimals rejected
7. category normalization
8. empty category rejected
9. missing description defaults to empty
10. transaction retains valid date
11. ledger adds/returns transaction
12. chronological listing
13. total income
14. total expenses
15. balance
16. type filter
17. category filter
18. inclusive date filter
19. reversed range rejected
20. empty ledger summary
21. month summary excludes other months
22. expense category grouping/order
23. database initialization
24. save assigns ID
25. save/reopen/load round trip
26. amount-cent round trip
27. stored filter
28. CLI add persists and prints success
29. CLI list prints table or empty result
30. CLI monthly summary totals
31. invalid CLI amount produces no record
32. CSV exact header and formatted amount
33. empty CSV is header-only

## 9. Verification commands

During development:

```bash
python -m pytest tests/ -q
python -m pytest tests/transaction_test.py -q
python -m pytest tests/ledger_test.py -q
```

End-to-end verification from a fresh database:

```bash
python -m finance --database /tmp/finance-demo.db add income 1500 salary "July salary" --date 2026-07-01
python -m finance --database /tmp/finance-demo.db add expense 12.50 food "Lunch" --date 2026-07-12
python -m finance --database /tmp/finance-demo.db list
python -m finance --database /tmp/finance-demo.db summary --month 2026-07
python -m finance --database /tmp/finance-demo.db export --month 2026-07 --output /tmp/july.csv
```

Expected totals are €1500.00 income, €12.50 expenses, and €1487.50 balance.

## 10. Definition of done

- [ ] A new user can follow README and use the app.
- [ ] Records survive restarts.
- [ ] Invalid data never reaches SQLite.
- [ ] Money never uses `float`.
- [ ] Every required command matches this guide.
- [ ] CSV format is exact.
- [ ] At least 30 meaningful tests pass.
- [ ] You can explain why domain, ledger, storage, reporting, and CLI are separate.
- [ ] Git excludes virtual environments, caches, and databases.
- [ ] You can demo add → list → summary → export from an empty database.

## First coding session

Implement **only Milestone 1** today:

1. Write one test for a valid income in `tests/transaction_test.py`.
2. Run it and confirm it fails because `Transaction` does not yet exist.
3. Implement the smallest `Transaction` needed to pass.
4. Rerun that test and the full suite.
5. Repeat separately for valid expense and zero amount rejection.
6. Stop and review before adding the next rule.

Before coding, answer this: **Why should `Ledger.add_transaction()` accept a complete `Transaction`, not separate amount/category/type values?**

Answer: a transaction owns the data and validation that define one financial event. A ledger should manage already-valid events instead of duplicating construction and validation logic.
