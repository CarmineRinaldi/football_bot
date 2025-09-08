import sqlite3
from datetime import datetime, timedelta
import os

DB_PATH = os.getenv("DATABASE_URL", "users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        vip INTEGER DEFAULT 0,
        free_matches INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tickets(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        ticket TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def save_ticket(user_id: int, ticket: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO tickets(user_id, ticket) VALUES (?,?)", (user_id, ticket))
    conn.commit()
    conn.close()

def get_tickets(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    expiry = datetime.now() - timedelta(hours=48)
    c.execute("DELETE FROM tickets WHERE created_at <= ?", (expiry,))
    c.execute("SELECT ticket FROM tickets WHERE user_id=?", (user_id,))
    tickets = [row[0] for row in c.fetchall()]
    conn.commit()
    conn.close()
    return tickets

def increment_free(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users(user_id) VALUES (?)", (user_id,))
    c.execute("UPDATE users SET free_matches = free_matches + 1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def get_free_count(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT free_matches FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0
