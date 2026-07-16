from transaction import Transaction
from decimal import Decimal
from datetime import date 

TYPE_TRANSACTIONS =["expense","income"]

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


    def list_transaction_type(self, transaction_type: str) -> list[Transaction]:
        arranged_list = self.list_transactions()
        type_list = []

        if transaction_type not in TYPE_TRANSACTIONS:
            raise ValueError("Transaction type incorrect value")


        for transaction in arranged_list:
            if transaction.transaction_type == transaction_type:
                type_list.append(transaction)

        return type_list


    # Return a list with based on amount (bigger is first)
    def list_transaction_amount(self) -> list[Transaction]:
        arranged_list = sorted(self.transactions, key = lambda transaction: transaction.amount, reverse = True)
        return arranged_list

    # using list_transactions list only one category
    # 3 options
    # 1. Only a category
    # 2. Only a month
    # 3 both category and month
    def list_category_transactions(self, category : str, month : int) -> list[Transaction]:
        list_trans = self.list_transactions()
        list_cat = []

        # Check
        if category == "" and (month <= 0 or month >= 13)  :
            raise ValueError("Neither category name or month was provided, error in list_category_transactions")

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

    # Return a list by date
    # Again 3 options 
    # 1 start date only 
    # 2 end date only 
    # 3 both start and end date 
    def list_transaction_date(
        self, 
        start_date : date | None = None, 
        end_date : date | None = None,
    ) -> list[Transaction]:

        arranged_list = []
        if start_date is not None and not isinstance(start_date, date):
            raise TypeError("start_date must be a date or None")
    
        if end_date is not None and not isinstance(end_date, date):
            raise TypeError("end_date must be a date or None")
    
        if start_date is not None and end_date is not None:
            if start_date > end_date:
                raise ValueError("start_date cannot be after end_date")

                
        if end_date == None :
            for transaction in self.transactions:
                if transaction.transaction_date >= start_date :
                    arranged_list.append(transaction)

        elif start_date == None : 
            for transaction in self.transactions:
                if transaction.transaction_date <= end_date:
                    arranged_list.append(transaction)


        else :
            for transaction in self.transactions:
                if transaction.transaction_date >= start_date and transaction.transaction_date <= end_date:
                    arranged_list.append(transaction)
            


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
