# db.py
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
DB_FILE = "bot.db"

# =========================
# Inizializza DB
# =========================
def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        
        # Tabella utenti
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            vip INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Tabella tickets/schedine
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)

        conn.commit()
        conn.close()
        logger.info("DB inizializzato correttamente.")
    except Exception as e:
        logger.exception("Errore inizializzazione DB: %s", e)
        raise e

# =========================
# Gestione utenti
# =========================
def add_user(user_id, username=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("""
        INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)
        """, (user_id, username))
        conn.commit()
        conn.close()
        logger.info("Utente aggiunto: %s (@%s)", user_id, username)
    except Exception as e:
        logger.exception("Errore add_user: %s", e)

def get_all_users():
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT id FROM users")
        users = [row[0] for row in cur.fetchall()]
        conn.close()
        return users
    except Exception as e:
        logger.exception("Errore get_all_users: %s", e)
        return []

def is_vip(user_id):
    """
    Controlla se un utente è VIP
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT vip FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return bool(row[0]) if row else False
    except Exception as e:
        logger.exception("Errore is_vip: %s", e)
        return False

# =========================
# Gestione tickets
# =========================
def add_ticket(user_id, ticket_data):
    """
    ticket_data: dict o qualsiasi struttura serializzabile JSON
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("INSERT INTO tickets (user_id, data) VALUES (?, ?)",
                    (user_id, json.dumps(ticket_data)))
        conn.commit()
        conn.close()
        logger.info("Ticket aggiunto per utente %s", user_id)
    except Exception as e:
        logger.exception("Errore add_ticket: %s", e)

def get_user_tickets(user_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT data, created_at FROM tickets WHERE user_id=? ORDER BY created_at DESC", (user_id,))
        tickets = [{"data": json.loads(row[0]), "created_at": row[1]} for row in cur.fetchall()]
        conn.close()
        return tickets
    except Exception as e:
        logger.exception("Errore get_user_tickets: %s", e)
        return []
