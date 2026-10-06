"""
Backend Database Layer
Manages SQLite database connections, table schema initialization, and transactional queries.
"""

import os
import sqlite3
from typing import Generator
from contextlib import contextmanager

# Determine base paths relative to this file
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
DB_DIR = os.path.join(PROJECT_ROOT, "database")
DB_FILE = os.path.join(DB_DIR, "app.db")

def init_db() -> str:
    """
    Initializes the SQLite database directory and creates tables if they do not exist.
    Returns the path to the database file.
    """
    os.makedirs(DB_DIR, exist_ok=True)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                age INTEGER NOT NULL,
                department TEXT NOT NULL,
                message TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT DEFAULT '127.0.0.1',
                user_agent TEXT DEFAULT 'Unknown'
            );
        """)
        
        # Create helpful index for faster queries and sorting
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_reg_submitted_at 
            ON student_registrations(submitted_at DESC);
        """)
        conn.commit()
        
    return DB_FILE

@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager that yields an active SQLite connection configured with
    sqlite3.Row row_factory for column-name based access and automatic rollback on error.
    """
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    path = init_db()
    print(f"[OK] Database initialized successfully at: {path}")
