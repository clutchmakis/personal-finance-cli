from argparse import ArgumentParser, Namespace
from datetime import date
from decimal import Decimal

from .transaction import Transaction
from .ledger import Ledger
from .storage import SQLiteStorage

def main(): 
    
    parser = ArgumentParser()

    _ = parser.add_argument('--database', help = 'Declare the path in which the following transaction will be stored', default = "data/finance.db")

    subparsers = parser.add_subparsers(dest ="command", required = True )

    add_parser = subparsers.add_parser("add")

    # Create the arguments, the "_=" removes the warnings of something getting returned and not use it 
    _ = add_parser.add_argument('transaction_type', help= "Declaring the type of amount: expense or income", type = str) 
    _ = add_parser.add_argument('amount', help= 'Value of amount', type = str)
    _ = add_parser.add_argument('category', help = 'Store the name of the category', type = str)
    _ = add_parser.add_argument('description', help = 'Description of transaction', type = str,default ="", nargs = '?')
    _ = add_parser.add_argument('--date', help = 'Date of transaction', type =str)
    
    # pass the values in the args
    args: Namespace = parser.parse_args()

    database = args.database 
    transaction_type : str = args.transaction_type
    amount = Decimal(args.amount)
    category : str = args.category
    description: str = args.description
    
    if args.date:
        try:
            transaction_date = date.fromisoformat(args.date)
        except ValueError:
            parser.error("date must use YYYY-MM-DD format")
    else :
        transaction_date = date.today()
    
    # Create the transaction
    
    new_transaction = Transaction(
        transaction_type=transaction_type,
        amount=amount,
        category=category,
        transaction_date=transaction_date,
        description=description,
    )   
    storage = SQLiteStorage(database)
    ledger = Ledger(storage)
    saved_transaction = ledger.add_transaction(new_transaction)

    print(f'Added {saved_transaction.transaction_type} #{saved_transaction.id}: €{saved_transaction.amount} in {saved_transaction.category} on {saved_transaction.transaction_date}.')

    