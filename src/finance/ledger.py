from transaction import Transaction
from decimal import Decimal

class Ledger:
    def __init__(self):
        self.transactions = []

    # We dont care if it is a transaction or not, the checks have been done
    def add_transaction(self, transaction: Transaction):
        if not isinstance(transaction, Transaction):
            raise TypeError("Ledger can only store Transactions  ")
        self.transactions.append(transaction)

    def list_transactions(self):
        arranged_list = sorted(self.transactions, key= lambda transaction: transaction.transaction_date)
        return arranged_list
        
    # Return Total expenses 
    def total_expenses(self):
        expense = Decimal("0.00")
        for transaction in self.transactions:
            if transaction.transaction_type == "expense":
                expense += transaction.amount

        return expense

   
    def total_income(self):
        income = Decimal("0.00")
        for transaction in self.transactions:
            if transaction.transaction_type == "income":
                income += transaction.amount

        return income 

    def balance(self):
        return self.total_income() - self.total_expenses()
