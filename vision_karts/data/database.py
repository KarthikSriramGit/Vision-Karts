"""
Database Abstraction Layer

Provides database interface for persistence (SQLite by default, can use PostgreSQL/MySQL).
"""

import logging
import sqlite3
from typing import List, Dict, Optional
from pathlib import Path
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class Database:
    """
    Database abstraction layer.
    """
    
    def __init__(self, db_path: str = "data/vision_karts.db"):
        """
        Initialize database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._initialize_database()
        
        logger.info(f"Database initialized: {db_path}")
    
    def _initialize_database(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Customers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id TEXT PRIMARY KEY,
                    name TEXT,
                    email TEXT,
                    phone TEXT,
                    payment_method TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_visit TIMESTAMP
                )
            """)
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    customer_id TEXT,
                    entry_time TIMESTAMP,
                    exit_time TIMESTAMP,
                    status TEXT,
                    entry_camera TEXT,
                    exit_camera TEXT,
                    cart_id TEXT,
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
                )
            """)
            
            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    customer_id TEXT,
                    timestamp TIMESTAMP,
                    total_amount REAL,
                    item_count INTEGER,
                    payment_status TEXT,
                    receipt_path TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
                )
            """)
            
            # Transaction items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transaction_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT,
                    product_name TEXT,
                    quantity INTEGER,
                    unit_price REAL,
                    total_price REAL,
                    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
                )
            """)
            
            # Analytics events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT,
                    customer_id TEXT,
                    session_id TEXT,
                    product_name TEXT,
                    value REAL,
                    timestamp TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            conn.commit()
            logger.info("Database schema initialized")
    
    @contextmanager
    def get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute SELECT query and return results."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_update(self, query: str, params: tuple = ()):
        """Execute INSERT/UPDATE/DELETE query."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
