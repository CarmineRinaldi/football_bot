import sqlite3
import os

DATABASE = os.getenv("DATABASE_URL", "users.db")

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            plan TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            match TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user_id, plan):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO users (user_id, plan) VALUES (?, ?)', (user_id, plan))
    conn.commit()
    conn.close()

def get_user_plan(user_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT plan FROM users WHERE user_id=?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def add_ticket(user_id, match):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT INTO tickets (user_id, match) VALUES (?, ?)', (user_id, match))
    conn.commit()
    conn.close()

def get_user_tickets(user_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT match FROM tickets WHERE user_id=?', (user_id,))
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]
