from dataclasses import dataclass
from transaction import Transaction
from decimal import Decimal
from datetime import date
from storage import SQLiteStorage


@dataclass
class Summary:
    income: Decimal
    expenses: Decimal
    balance: Decimal
    expense_categories: list[tuple[str, Decimal]]


class Ledger:
    def __init__(self, storage : SQLiteStorage):
        self.storage = storage

    # We dont care if it is a transaction or not, the checks have been done
    def add_transaction(self, transaction: Transaction) -> Transaction:
        if not isinstance(transaction, Transaction):
            raise TypeError("Ledger can only store Transactions  ")

        return self.storage.save(transaction)


    def list_transactions(
        self,
        transaction_type: str | None = None,
        category : str | None = None,
        start_date : date | None = None,
        end_date : date | None = None,
    ) -> list[Transaction]:
        caller_list = self.storage.list_transactions(
            transaction_type,
            category,
            start_date,
            end_date,
        )

        return caller_list

    def summary(self, month:str | None = None ) -> Summary :
        income = Decimal("0.00")
        expense = Decimal("0.00")
        expense_categories : dict[str, Decimal] = {}

        # Bring the list of transactions from the Storage
        transactions = self.storage.list_transactions()


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
            for transaction in transactions:
                if selected_month == transaction.transaction_date.month and selected_year == transaction.transaction_date.year:
                    if transaction.transaction_type == "income":
                        income += transaction.amount

        else:
            for transaction in transactions:
                if transaction.transaction_type == "income":
                    income += transaction.amount

        # For expenses
        expense = Decimal("0.00")

        if selected_month :
            for transaction in transactions:
                if selected_month == transaction.transaction_date.month and selected_year == transaction.transaction_date.year:
                    if transaction.transaction_type == "expense":
                        expense += transaction.amount

        else :
            for transaction in transactions:
                if transaction.transaction_type == "expense":
                    expense += transaction.amount

        # For balance
        balance = income - expense


        # For expense Categories
        if selected_month:
            for transaction in transactions:
                if transaction.transaction_type == "expense" and transaction.transaction_date.month == selected_month and transaction.transaction_date.year == selected_year :
                    # Creating the category if it does not exist, current total will have the value of the corresponding category (e.g. food)
                    current_total = expense_categories.get(transaction.category,Decimal("0.00"))

                    # Add the new amount of the last transaction
                    new_total = current_total + transaction.amount

                    # And then put it in the dictionary
                    expense_categories[transaction.category] = new_total

        else :
            for transaction in transactions:
                if transaction.transaction_type == "expense"  :
                    # Creating the category if it does not exist, current total will have the value of the corresponding category (e.g. food)
                    current_total = expense_categories.get(transaction.category,Decimal("0.00"))

                    # Add the new amount of the last transaction
                    new_total = current_total + transaction.amount

                    # And then put it in the dictionary
                    expense_categories[transaction.category] = new_total

        ordered_categories = list(sorted(expense_categories.items(), key = lambda item : (-item[1], item[0]),))
        return Summary(income,expense,balance,ordered_categories)
