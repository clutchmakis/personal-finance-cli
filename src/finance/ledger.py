from dataclasses import dataclass
from transaction import Transaction
from decimal import Decimal
from datetime import date

TYPE_TRANSACTIONS =["expense","income"]

@dataclass
class Summary:
    income: Decimal
    expenses: Decimal
    balance: Decimal
    expense_categories: list[tuple[str, Decimal]]


class Ledger:
    def __init__(self):
        self.transactions = []

    # We dont care if it is a transaction or not, the checks have been done
    def add_transaction(self, transaction: Transaction) -> None:
        if not isinstance(transaction, Transaction):
            raise TypeError("Ledger can only store Transactions  ")
        self.transactions.append(transaction)



    def list_transactions(
        self,
        transaction_type: str | None = None,
        category : str | None = None,
        start_date : date | None = None,
        end_date : date | None = None,
    ) -> list[Transaction]:

        arranged_list = sorted(self.transactions, key= lambda transaction: transaction.transaction_date)
        caller_list = []
        flag = 0

        # 1st filter
        if transaction_type is not None :
            if transaction_type not in TYPE_TRANSACTIONS:
                raise ValueError("Transaction type incorrect value")

            for transaction in arranged_list:
                if transaction.transaction_type != transaction_type:
                            continue
                if transaction.transaction_type == transaction_type:
                    caller_list.append(transaction)
            flag = 1


        # 2rd
        if category is not None :

            if category:
                category = category.strip().lower()

            
            if category == "" :
                raise ValueError("Category name invalid")

            # This is the AND if flag = 1 then the caller_list is not empty 
            if flag == 1 :
                arranged_list = caller_list.copy()
                caller_list =[]
            else :
                flag = 1
                
            for transaction in arranged_list:
                if transaction.category != category :
                    continue
            # 1st option
            
                caller_list.append(transaction)

        # 3th
        if start_date or end_date :
            if start_date is not None and not isinstance(start_date, date):
                raise TypeError("start_date must be a date or None")

            if end_date is not None and not isinstance(end_date, date):
                raise TypeError("end_date must be a date or None")

            if start_date is not None and end_date is not None:
                if start_date > end_date:
                    raise ValueError("start_date cannot be after end_date")

            if flag == 1 :
                arranged_list = caller_list.copy()
                caller_list =[]
            else :
                flag = 1

            if end_date is None :
                for transaction in arranged_list:
                    if start_date > transaction.transaction_date:
                        continue
                    if transaction.transaction_date >= start_date :
                        caller_list.append(transaction)

            elif start_date is None :
                for transaction in arranged_list:
                    if end_date < transaction.transaction_date:
                        continue
                    if transaction.transaction_date <= end_date:
                        caller_list.append(transaction)


            else :
                for transaction in arranged_list:
                    if start_date > transaction.transaction_date and end_date < transaction.transaction_date:
                        continue

                    if transaction.transaction_date >= start_date and transaction.transaction_date <= end_date:
                        caller_list.append(transaction)


        # In case list_transactions takes no argument
        if not transaction_type  and not category and not start_date and not end_date:
            caller_list = arranged_list.copy()

        return caller_list

    def summary(self, month:str | None = None ) :
        income = Decimal("0.00")
        expense = Decimal("0.00")
        expense_categories : dict[str, Decimal] = {}
        
        selected_year = None
        selected_month = None
        
        if month is not None:
            try:
                selected_date = date.fromisoformat(f"{month}-01")
            except (TypeError, ValueError) as error:
                raise ValueError("Month must be in YYYY-MM format") from error
        
            if selected_date.strftime("%Y-%m") != month:
                raise ValueError("Month must be in YYYY-MM format")
        
            selected_year = selected_date.year
            selected_month = selected_date.month
        
        # For income 
        if selected_month :
            for transaction in self.transactions:
                if selected_month == transaction.transaction_date.month and selected_year == transaction.transaction_date.year:
                    if transaction.transaction_type == "income":
                        income += transaction.amount

        else:
            for transaction in self.transactions:
                if transaction.transaction_type == "income":
                    income += transaction.amount

        # For expenses 
        expense = Decimal("0.00")

        if selected_month :
            for transaction in self.transactions:
                if selected_month == transaction.transaction_date.month and selected_year == transaction.transaction_date.year:
                    if transaction.transaction_type == "expense":
                        expense += transaction.amount

        else :
            for transaction in self.transactions:
                if transaction.transaction_type == "expense":
                    expense += transaction.amount

        # For balance 
        balance = income - expense 


        # For expense Categories 
        if selected_month:
            for transaction in self.transactions:
                if transaction.transaction_type == "expense" and transaction.transaction_date.month == selected_month and transaction.transaction_date.year == selected_year :
                    # Creating the category if it does not exist, current total will have the value of the corresponding category (e.g. food)
                    current_total = expense_categories.get(transaction.category,Decimal("0.00"))

                    # Add the new amount of the last transaction
                    new_total = current_total + transaction.amount

                    # And then put it in the dictionary
                    expense_categories[transaction.category] = new_total

        else :
            for transaction in self.transactions:
                if transaction.transaction_type == "expense"  :
                    # Creating the category if it does not exist, current total will have the value of the corresponding category (e.g. food)
                    current_total = expense_categories.get(transaction.category,Decimal("0.00"))

                    # Add the new amount of the last transaction
                    new_total = current_total + transaction.amount

                    # And then put it in the dictionary
                    expense_categories[transaction.category] = new_total

        ordered_categories = list(sorted(expense_categories.items(), key = lambda item : (-item[1], item[0]),))
        return Summary(income,expense,balance,ordered_categories)

        
        




