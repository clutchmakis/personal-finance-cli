from argparse import ArgumentParser, Namespace
from datetime import date
from decimal import Decimal, InvalidOperation

from .ledger import Ledger, Summary
from .reporting import format_summary_table, format_transaction_table
from .storage import SQLiteStorage
from .transaction import Transaction


def summary_command(args: Namespace, ledger:Ledger) -> None:
    # There is no reason for us to check whether month exists as it is checked in ledger
    summary: Summary = ledger.summary(args.month)
    print(format_summary_table(summary,args.month))


def list_command(args: Namespace, ledger: Ledger) -> None:
    if args.start_date:
        start_date = date.fromisoformat(args.start_date)
    else:
        start_date = None

    if args.end_date:
        end_date = date.fromisoformat(args.end_date)
    else:
        end_date = None

    transaction_list = ledger.list_transactions(
        transaction_type=args.type,
        category=args.category,
        start_date=start_date,
        end_date=end_date,
    )

    print(format_transaction_table(transaction_list))

def add_command(args : Namespace, ledger: Ledger) -> None:

    transaction_type = args.transaction_type

    # Check if the amount is type Decimal
    try:
        amount = Decimal(args.amount)
    except InvalidOperation as error:
        raise ValueError("Amount must be a valid decimal number") from error

    category = args.category
    description = args.description

    # Check the date to be a date
    if args.date:
        try:
            transaction_date = date.fromisoformat(args.date)
        except ValueError as error:
            raise ValueError(
                "Date must use YYYY-MM-DD format"
            ) from error
    else:
        transaction_date = date.today()

    # Create the transaction
    new_transaction = Transaction(
        transaction_type=transaction_type,
        amount=amount,
        category=category,
        transaction_date=transaction_date,
        description=description,
    )

    saved_transaction = ledger.add_transaction(new_transaction)

    print(f'Added {saved_transaction.transaction_type} #{saved_transaction.id}: €{format(saved_transaction.amount,".2f")} in {saved_transaction.category} on {saved_transaction.transaction_date}.')


def main() -> None:

    parser = ArgumentParser()
    _ = parser.add_argument(
            '-d',
            '--database',
            help = 'Declare the path in which the following transaction will be stored',
            default = "data/finance.db"
    )

    subparsers = parser.add_subparsers(dest ="command", required = True )
    add_parser = subparsers.add_parser("add")
    list_parser = subparsers.add_parser("list")
    summary_parser = subparsers.add_parser("summary")

    # Create the arguments, the "_=" removes the warnings of something getting returned and not use it
    _ = add_parser.add_argument(
                'transaction_type',
                help= "Declaring the type of amount: expense or income",
        )
    _ = add_parser.add_argument(
                'amount',
                help= 'Value of amount'
        )
    _ = add_parser.add_argument(
                'category',
                help = 'Store the name of the category'
        )
    _ = add_parser.add_argument(
                'description',
                help = 'Description of transaction',
                default ="",
                nargs = '?'
        )
    _ = add_parser.add_argument(
                '--date',
                help = 'Date of transaction',
        )

    _ = list_parser.add_argument(
        '--type',
        help='List transactions based on type',
    )

    _ = list_parser.add_argument(
        '--category',
        help='List transactions based on category',
    )

    _ = list_parser.add_argument(
        '--start-date',
        help='List transactions from that day',
    )

    _ = list_parser.add_argument(
        '--end-date',
        help='List transactions until that day',
    )

    _ = summary_parser.add_argument(
        '--month',
        help='Add the month for the summary to calculate'
    )
    args : Namespace = parser.parse_args()
    ledger = Ledger(SQLiteStorage(args.database))

    try:
        if args.command == "add":
            add_command(args, ledger)
        elif args.command == "list":
            list_command(args, ledger)
        elif args.command == "summary":
            summary_command(args,ledger)
    except ValueError as error:
        parser.error(str(error))
