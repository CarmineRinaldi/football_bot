import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.getenv("DATABASE_URL", "users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    plan TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    matches TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                 )''')
    conn.commit()
    conn.close()

def add_user(user_id, plan="free"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, plan) VALUES (?, ?)", (user_id, plan))
    conn.commit()
    conn.close()

def get_user_plan(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT plan FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def add_ticket(user_id, matches):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO tickets (user_id, matches) VALUES (?, ?)", (user_id, ",".join(matches)))
    conn.commit()
    conn.close()

def get_user_tickets(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, matches, created_at FROM tickets WHERE user_id=?", (user_id,))
    tickets = c.fetchall()
    conn.close()
    return tickets

def delete_old_tickets(days=1):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    cutoff = datetime.utcnow() - timedelta(days=days)
    c.execute("DELETE FROM tickets WHERE created_at < ?", (cutoff,))
    conn.commit()
    conn.close()
