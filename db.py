import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.getenv("DATABASE_URL", "users.db")

# --------------------------
# Inizializzazione DB
# --------------------------
def init_db():
    """Crea le tabelle 'users' e 'tickets' se non esistono."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                plan TEXT DEFAULT 'free',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                matches TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        conn.commit()

# --------------------------
# Gestione utenti
# --------------------------
def add_user(user_id, plan="free"):
    """Aggiunge un nuovo utente o ignora se esiste già."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO users (user_id, plan) VALUES (?, ?)",
            (user_id, plan)
        )
        conn.commit()

def get_user_plan(user_id):
    """Restituisce il piano dell'utente, se esiste."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT plan FROM users WHERE user_id=?", (user_id,))
        result = c.fetchone()
    return result[0] if result else None

# --------------------------
# Gestione tickets
# --------------------------
def add_ticket(user_id, matches):
    """Aggiunge una schedina per l'utente."""
    if not matches:
        return
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO tickets (user_id, matches) VALUES (?, ?)",
            (user_id, ",".join(matches))
        )
        conn.commit()

def get_user_tickets(user_id):
    """Recupera tutte le schedine dell'utente."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            "SELECT id, matches, created_at FROM tickets WHERE user_id=? ORDER BY created_at DESC",
            (user_id,)
        )
        tickets = c.fetchall()
    return tickets

def delete_old_tickets(days=1):
    """Elimina schedine più vecchie di 'days' giorni."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM tickets WHERE created_at < ?", (cutoff,))
        conn.commit()
