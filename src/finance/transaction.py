# The transaction class
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

TRANSACTION_TYPES = ("expense", "income")


@dataclass
class Transaction:
    transaction_type: str
    amount: Decimal  # create with Decimal("number")
    category: str
    description: str # Probably must be "description = "" "
    transaction_date: date
    id: int | None = None

    def __post_init__(self) -> None:

        # TRANSACTION
        # Check if the transaction is a string (not a number or empy) This is probably not needed but let it be
        if not isinstance(self.transaction_type, str):
            raise TypeError("Transaction type must be a string")

        # Check if empty
        if not self.transaction_type.strip():
            raise ValueError("Transaction type can not be empty")

        self.transaction_type = self.transaction_type.strip().lower()

        # Check if the transaction is either Expence or Income type
        if self.transaction_type not in TRANSACTION_TYPES:
            raise ValueError(f"{self.transaction_type} is not Expense or Income")


        # AMOUNT
        # Check if the amount is type Decimal
        if not isinstance(self.amount, Decimal):
            raise TypeError("Amount in not a Decimal Type")

        # Check if it is a number or not
        if not self.amount.is_finite():
            raise ValueError("Amount must be a finite number")

        # Check if amount is negative or zero
        if self.amount <= Decimal(0):
            raise ValueError(f"{self.amount} is negative or zero number")

        exponent = self.amount.as_tuple().exponent

        # Check whether the exponent is a number (-2,-3...) and not a letter (n,f) and then check if it is .00 and not bigger 
        if not isinstance(exponent, int):
            raise ValueError("Amount must have a valid decimal exponent")
        
        if exponent < -2:
            raise ValueError("Amount cannot have more than two decimal places")


        # CATEGORY
        # Check if category is a string the list will be create by user 
        if not isinstance(self.category, str):
            raise TypeError(f"{self.category} is not a string")

        self.category = self.category.strip().lower()

        # Then check if it is empty
        if not self.category:
            raise ValueError("Category can not be empty")


        # DESCRIPTION
        # Check only if description is a string
        if not isinstance(self.description, str):
            raise TypeError("Description is not a string")

        self.description = self.description.strip()

        
        # DATE
        # Check the date to be a date
        if not isinstance(self.transaction_date, date):
            raise TypeError("Date input is not an actual date type")
