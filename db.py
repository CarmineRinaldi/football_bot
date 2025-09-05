import sqlite3
from datetime import datetime, timedelta
import os

DB_PATH = os.environ.get("DATABASE_URL", "users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                 chat_id INTEGER PRIMARY KEY,
                 plan TEXT DEFAULT 'free',
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 )""")
    c.execute("""CREATE TABLE IF NOT EXISTS tickets (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 chat_id INTEGER,
                 matches TEXT,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 )""")
    conn.commit()
    conn.close()

def get_user(chat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(chat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO users (chat_id) VALUES (?)", (chat_id,))
    conn.commit()
    conn.close()

def save_ticket(chat_id, matches):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO tickets (chat_id, matches) VALUES (?, ?)", (chat_id, matches))
    conn.commit()
    conn.close()

def get_tickets(chat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM tickets WHERE chat_id=?", (chat_id,))
    tickets = c.fetchall()
    conn.close()
    return tickets

def delete_old_tickets():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    cutoff = datetime.now() - timedelta(days=10)
    c.execute("DELETE FROM tickets WHERE created_at < ?", (cutoff,))
    conn.commit()
    conn.close()

# init db on start
init_db()
