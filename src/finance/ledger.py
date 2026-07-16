from transaction import Transaction
from decimal import Decimal

class Ledger:
    def __init__(self):
        self.transactions = []

    # We dont care if it is a transaction or not, the checks have been done
    def add_transaction(self, transaction: Transaction) -> None:
        if not isinstance(transaction, Transaction):
            raise TypeError("Ledger can only store Transactions  ")
        self.transactions.append(transaction)

    def list_transactions(self) -> list[Transaction]:
        arranged_list = sorted(self.transactions, key= lambda transaction: transaction.transaction_date)
        return arranged_list

    # Return a list with based on amount (bigger is first)
    def list_transaction_amount(self) -> list[Transaction]:
        arranged_list = sorted(self.transactions, key = lambda transaction: transaction.amount, reverse = True)
        return arranged_list

    # using list_transactions list only one category 
    # 3 options 
    # 1. Only a category 
    # 2. Only a month 
    # 3 both categort and month 
    def list_category_transactions(self, category : str, month : int) -> list[Transaction]:
        list_trans = self.list_transactions()
        list_cat = []
        for transaction in list_trans:
            # 1st option 
            if month == 0:
                if transaction.category == category  :
                    list_cat.append(transaction)

            # 2nd option 
            elif category == "":
                if transaction.transaction_date.month  == month  :
                    list_cat.append(transaction)

            # 3rd option 
            else : 
                if transaction.category == category and transaction.transaction_date.month  == month:
                    list_cat.append(transaction)

        return list_cat
        
    
    def total_expenses(self) -> Decimal:
        expense = Decimal("0.00")
        for transaction in self.transactions:
            if transaction.transaction_type == "expense":
                expense += transaction.amount

        return expense

   
    def total_income(self) -> Decimal:
        income = Decimal("0.00")
        for transaction in self.transactions:
            if transaction.transaction_type == "income":
                income += transaction.amount

        return income 

    def balance(self) -> Decimal:
        return self.total_income() - self.total_expenses()
