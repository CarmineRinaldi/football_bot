import sqlite3
from contextlib import closing
import os

DB_PATH = os.environ.get("DATABASE_URL", "users.db")

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                plan TEXT,
                last_request TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                match_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def add_ticket(user_id, match_data):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO tickets (user_id, match_data) VALUES (?,?)", (user_id, match_data))
        conn.commit()

def get_tickets(user_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT match_data FROM tickets 
            WHERE user_id=? AND created_at > datetime('now','-2 day')
        """, (user_id,))
        return [row[0] for row in c.fetchall()]
