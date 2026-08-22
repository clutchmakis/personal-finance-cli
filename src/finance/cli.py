from datetime import date
from .ledger import Ledger
from .storage import SQLiteStorage
from .transaction import Transaction
from .reporting import format_transaction_table
from decimal import Decimal, InvalidOperation
from argparse import ArgumentParser, Namespace



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

    args : Namespace = parser.parse_args()
    ledger = Ledger(SQLiteStorage(args.database))

    try:
        if args.command == "add":
            add_command(args, ledger)
        elif args.command == "list":
            list_command(args, ledger)
    except ValueError as error:
        parser.error(str(error))
