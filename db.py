import sqlite3
from datetime import datetime, timedelta

DB_FILE = "football_bot.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Utenti
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        created_at TEXT
    )
    """)

    # Tickets / pronostici
    c.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        match_id INTEGER,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, created_at) VALUES (?, ?)", 
              (user_id, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def add_ticket(user_id, match_ids):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for match_id in match_ids:
        c.execute("INSERT INTO tickets (user_id, match_id, created_at) VALUES (?, ?, ?)",
                  (user_id, match_id, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_user_tickets(user_id):
    """Restituisce solo i ticket fatti oggi"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    c.execute("SELECT match_id FROM tickets WHERE user_id=? AND created_at>=?", 
              (user_id, today_start.isoformat()))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def can_add_prediction(user_id):
    """Verifica se l'utente può aggiungere un pronostico oggi (max 5)"""
    tickets_today = get_user_tickets(user_id)
    return len(tickets_today) < 5

def delete_old_tickets():
    """Pulizia dei ticket vecchi di più di 1 giorno"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    yesterday = datetime.utcnow() - timedelta(days=1)
    c.execute("DELETE FROM tickets WHERE created_at<?", (yesterday.isoformat(),))
    conn.commit()
    conn.close()
