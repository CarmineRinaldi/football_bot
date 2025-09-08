import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.getenv("DATABASE_URL", "users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Utenti e piano
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER UNIQUE,
        plan TEXT,
        last_request TIMESTAMP
    )""")
    # Schedine memorizzate
    c.execute("""CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        ticket TEXT,
        created_at TIMESTAMP
    )""")
    conn.commit()
    conn.close()

def save_ticket(user_id, ticket):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO tickets (user_id, ticket, created_at) VALUES (?, ?, ?)",
              (user_id, ticket, datetime.now()))
    conn.commit()
    conn.close()

def get_tickets(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ticket, created_at FROM tickets WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    # Filtra ticket più vecchi di 48h
    result = [t for t, created_at in rows if datetime.now() - datetime.fromisoformat(created_at) < timedelta(hours=48)]
    return result
