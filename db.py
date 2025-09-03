import sqlite3
import logging
import json
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
            data TEXT,  -- JSON con {"predictions": [...]}
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

def is_vip_user(user_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT vip FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return bool(row[0]) if row else False
    except Exception as e:
        logger.exception("Errore is_vip_user: %s", e)
        return False

def set_vip(user_id, vip_status=1):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("UPDATE users SET vip=? WHERE id=?", (vip_status, user_id))
        conn.commit()
        conn.close()
        logger.info("Utente %s aggiornato VIP=%s", user_id, vip_status)
    except Exception as e:
        logger.exception("Errore set_vip: %s", e)

# =========================
# Gestione tickets
# =========================
def add_ticket(user_id, ticket_data):
    """
    ticket_data deve essere una lista di pronostici (es: ["Juventus vs Milan → 1", "Roma vs Inter → X"])
    Salviamo sempre come {"predictions": [...]} per uniformità
    """
    try:
        normalized = {"predictions": ticket_data}
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("INSERT INTO tickets (user_id, data) VALUES (?, ?)",
                    (user_id, json.dumps(normalized)))
        conn.commit()
        conn.close()
        logger.info("Ticket aggiunto per utente %s", user_id)
    except Exception as e:
        logger.exception("Errore add_ticket: %s", e)

def get_user_tickets(user_id, date_filter=None):
    """
    Recupera le schedine di un utente.
    Se date_filter è passato (YYYY-MM-DD), ritorna solo quelle del giorno.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        if date_filter:
            cur.execute(
                "SELECT data, created_at FROM tickets WHERE user_id=? AND date(created_at)=? ORDER BY created_at DESC",
                (user_id, date_filter),
            )
        else:
            cur.execute(
                "SELECT data, created_at FROM tickets WHERE user_id=? ORDER BY created_at DESC",
                (user_id,),
            )
        rows = cur.fetchall()
        conn.close()

        tickets = []
        for row in rows:
            try:
                data = json.loads(row[0])
                preds = data.get("predictions", [])
            except Exception:
                preds = []
            tickets.append({
                "predictions": preds,
                "created_at": row[1]
            })
        return tickets
    except Exception as e:
        logger.exception("Errore get_user_tickets: %s", e)
        return []
