# The transaction class
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

Transaction_types = ["expense", "income"]

@dataclass
class Transaction:
    transaction_type: str
    amount : Decimal # create with Decimal("number")
    category: str
    description: str
    transaction_date : date
    id : int | None = None

    def __post_init__(self) -> None:

        # Check if the transaction is a string (not a number or empy)
        if not isinstance(self.transaction_type,str) :
            raise TypeError("Transaction type must be a string")

        if  self.transaction_type.lower() not in Transaction_types :
            raise ValueError(f"{self.transaction_type} is not Expense or Income")

        if self.amount <= Decimal(0):
            raise ValueError(f"{self.amount} is negative or zero ")
