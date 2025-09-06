# db.py
import sqlite3
from datetime import datetime, timedelta

DB_FILE = "football_bot.db"

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            plan TEXT DEFAULT 'free'
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS ticket_matches (
            ticket_id INTEGER,
            match_id INTEGER,
            prediction TEXT
        )
    """)
    conn.commit()
    conn.close()

def delete_old_tickets():
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM tickets WHERE created_at < ?", (datetime.now() - timedelta(days=7),))
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def get_user_plan(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT plan FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row["plan"] if row else "free"

def add_ticket(user_id, matches):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO tickets (user_id) VALUES (?)", (user_id,))
    ticket_id = c.lastrowid
    for match_id, prediction in matches.items():
        c.execute("INSERT INTO ticket_matches (ticket_id, match_id, prediction) VALUES (?, ?, ?)",
                  (ticket_id, match_id, prediction))
    conn.commit()
    conn.close()
    return ticket_id

def get_user_tickets(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM tickets WHERE user_id = ?", (user_id,))
    tickets = c.fetchall()
    conn.close()
    return tickets

def add_match_prediction(user_id, match_id, prediction):
    # Salva la previsione provvisoria per la schedina in creazione
    # Qui possiamo gestirla come ticket temporaneo
    return {"status": "ok", "user_id": user_id, "match_id": match_id, "prediction": prediction}
