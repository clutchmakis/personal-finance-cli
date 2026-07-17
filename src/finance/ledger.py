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


    # TODO:  implement all this functions of the list, inside the list_transactions method

    def list_transactions(
        self,
        transaction_type: str | None = None,
        amount_bool : bool | None = None,
        category : str | None = None,
        month : int | None = None,
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

        # 2nd filter
        if amount_bool:
            caller_list = sorted(caller_list, key = lambda transaction: transaction.amount, reverse = True)

        # 3rd
        if category or month :

            if category:
                category = category.strip().lower()

            if month is not None :
                if not isinstance(month, int) :
                    raise TypeError("Month in not a number ")

                elif month <1 or month > 12 :
                    raise ValueError("Month must be between 1-12 ")

            if category == "" :
                raise ValueError("Category name invalid")

            # This is the AND if flag = 1 then the caller_list is not empty 
            if flag == 1 :
                arranged_list = caller_list.copy()
                caller_list =[]
            else :
                flag = 1
                
            for transaction in arranged_list:
                if month is None:
                    if transaction.category != category and month :
                        continue
                # 1st option
                
                    if transaction.category == category  :
                        caller_list.append(transaction)

                # 2nd option
                elif category is None:
                    if transaction.transaction_date.month  == month  :
                        caller_list.append(transaction)

                # 3rd option
                else :
                    if transaction.category == category and transaction.transaction_date.month  == month:
                        caller_list.append(transaction)

        # 4th
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
        if not transaction_type and not amount_bool and not category and not month and not start_date and not end_date:
            caller_list = arranged_list.copy()

        return caller_list




    class Summary:
        def __init__(self, ledger: "Ledger", month: int |None = None) :
            self.ledger = ledger
            self.month = month

        def __post_init__(self):
            if self.month :
                if self.month <= 0 or self.month > 12 :
                    raise ValueError("Int of month must be between 1-12")

        def income(self) -> Decimal:
            income = Decimal("0.00")

            if self.month :
                for transaction in self.ledger.transactions:
                    if self.month == transaction.transaction_date.month :
                        if transaction.transaction_type == "income":
                            income += transaction.amount

            else:
                for transaction in self.ledger.transactions:
                    if transaction.transaction_type == "income":
                        income += transaction.amount

            return income

        def expenses(self) -> Decimal:
            expense = Decimal("0.00")

            if self.month :
                for transaction in self.ledger.transactions:
                    if self.month == transaction.transaction_date.month :
                        if transaction.transaction_type == "expense":
                            expense += transaction.amount

            else :
                for transaction in self.ledger.transactions:
                    if transaction.transaction_type == "expense":
                        expense += transaction.amount

            return expense

        def balance(self) -> Decimal:
            return self.income() - self.expenses()


        def expense_categories(self) -> list:
            amount_by_category = {}

            if self.month:
                for transaction in self.ledger.transactions:
                    if transaction.transaction_type == "expense" and transaction.transaction_date.month == self.month :
                        # Creating the category if it does not exist, current total will have the value of the corresponding category (e.g. food)
                        current_total = amount_by_category.get(transaction.category,Decimal("0.00"))

                        # Add the new amount of the last transaction
                        new_total = current_total + transaction.amount

                        # And then put it in the dictionary
                        amount_by_category[transaction.category] = new_total

            else :
                for transaction in self.ledger.transactions:
                    if transaction.transaction_type == "expense"  :
                        # Creating the category if it does not exist, current total will have the value of the corresponding category (e.g. food)
                        current_total = amount_by_category.get(transaction.category,Decimal("0.00"))

                        # Add the new amount of the last transaction
                        new_total = current_total + transaction.amount

                        # And then put it in the dictionary
                        amount_by_category[transaction.category] = new_total

            
            return list(sorted(amount_by_category.items(),key = lambda item: (-item[1],item[0])))
