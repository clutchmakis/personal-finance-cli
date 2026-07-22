import sqlite3
from decimal import Decimal
from src.finance.transaction import Transaction


class SQLiteStorage:
    def __init__(self, database_path: str, ):
        self.database_path = database_path


        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        # Create transaction table
        cursor.execute("""CREATE TABLE IF NOT EXISTS transactions(
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

        cursor.execute("""
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

        conn.close()
        

    def list_transactions(self) -> list :
        return []
