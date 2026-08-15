import sqlite3
from decimal import Decimal
from .transaction import Transaction
from datetime import date 
from pathlib import Path

TYPES_TRANSACTION = ("expense", "income")

class SQLiteStorage:
    def __init__(self, database_path: str, ):
        # Create the folders and the database 
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)


        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        # Create transaction table
        _=cursor.execute("""CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY,
            transaction_type TEXT NOT NULL CHECK (transaction_type IN('income', 'expense')),
            amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
            category TEXT NOT NULL CHECK (length(category)>0),
            description TEXT NOT NULL DEFAULT '',
            transaction_date TEXT NOT NULL
            );
        """)



        conn.close()

    def save(self, transaction:Transaction):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        _=cursor.execute("""
            INSERT INTO transactions(
            transaction_type,
            amount_cents,
            category,
            description,
            transaction_date
            ) VALUES(?,?,?,?,?)""",
            (
                transaction.transaction_type,
                int(transaction.amount * Decimal("100")) ,
                transaction.category,
                transaction.description,
                transaction.transaction_date.isoformat()
                )
            )

        # Return ID
        saved_id = cursor.lastrowid

        conn.commit()
        conn.close()
        saved_transaction = Transaction(
            transaction_type= transaction.transaction_type,
            amount= transaction.amount,
            category= transaction.category,
            description= transaction.description,
            transaction_date= transaction.transaction_date,
            id = saved_id)
        return saved_transaction


    def list_transactions(
        self,
        transaction_type: str | None = None,
        category: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Transaction]:
        conditions = []
        parameters = []
    
        if transaction_type is not None:
            if transaction_type not in TYPES_TRANSACTION:
                raise ValueError("Transaction type must be either expense or income")
    
            conditions.append("transaction_type = ?")
            parameters.append(transaction_type)
    
        if category is not None:
            if not isinstance(category, str):
                raise TypeError("Category name must be a string")
    
            category = category.strip().lower()
    
            if not category:
                raise ValueError("Category name invalid")
    
            conditions.append("category = ?")
            parameters.append(category)
    
        if start_date is not None and not isinstance(start_date, date):
            raise TypeError("start_date must be a date or None")
    
        if end_date is not None and not isinstance(end_date, date):
            raise TypeError("end_date must be a date or None")
    
        if start_date is not None and end_date is not None:
            if start_date > end_date:
                raise ValueError("start_date cannot be after end_date")
    
        if start_date is not None:
            conditions.append("transaction_date >= ?")
            parameters.append(start_date.isoformat())
    
        if end_date is not None:
            conditions.append("transaction_date <= ?")
            parameters.append(end_date.isoformat())
    
        where_clause = ""
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
    
        statement = (
            "SELECT id, transaction_type, amount_cents, category, "
            "description, transaction_date "
            "FROM transactions"
            f"{where_clause} "
            "ORDER BY transaction_date ASC, id ASC"
        )
    
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(statement, parameters).fetchall()
    
        transaction_list = []
    
        for row in rows:
            transaction_list.append(
                Transaction(
                    id=row[0],
                    transaction_type=row[1],
                    amount=Decimal(row[2]).scaleb(-2),
                    category=row[3],
                    description=row[4],
                    transaction_date=date.fromisoformat(row[5]),
                )
            )
    
        return transaction_list
