import sqlite3
import json
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
            plan TEXT DEFAULT 'free',       -- free / vip / pay
            ticket_quota INTEGER DEFAULT 0, -- solo per pay
            categories TEXT DEFAULT '[]',   -- lista JSON
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Tabella tickets/schedine
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            data TEXT,  -- JSON con {"predictions": [...], "category": "..."}
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
# Utenti
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

def get_user(user_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT id, username, vip, plan, ticket_quota, categories FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return {}
        return {
            "id": row[0],
            "username": row[1],
            "vip": row[2],
            "plan": row[3],
            "ticket_quota": row[4],
            "categories": json.loads(row[5])
        }
    except Exception as e:
        logger.exception("Errore get_user: %s", e)
        return {}

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
    user = get_user(user_id)
    return bool(user.get("vip", 0))

def set_vip(user_id, vip=1):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("UPDATE users SET vip=? WHERE id=?", (vip, user_id))
        conn.commit()
        conn.close()
        logger.info("Utente %s impostato VIP=%s", user_id, vip)
    except Exception as e:
        logger.exception("Errore set_vip: %s", e)

def set_plan(user_id, plan, ticket_quota=0, categories=None):
    """Imposta piano e opzioni dell’utente"""
    try:
        categories_json = json.dumps(categories or [])
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("""
        UPDATE users SET plan=?, ticket_quota=?, categories=? WHERE id=?
        """, (plan, ticket_quota, categories_json, user_id))
        conn.commit()
        conn.close()
        logger.info("Utente %s aggiornato piano=%s, ticket_quota=%s, categories=%s",
                    user_id, plan, ticket_quota, categories)
    except Exception as e:
        logger.exception("Errore set_plan: %s", e)

def decrement_ticket_quota(user_id, n=1):
    """Decrementa quota ticket Pay"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("UPDATE users SET ticket_quota = ticket_quota - ? WHERE id=? AND ticket_quota>=?", (n, user_id, n))
        conn.commit()
        conn.close()
        logger.info("Decrementata quota ticket Pay per utente %s di %s", user_id, n)
    except Exception as e:
        logger.exception("Errore decrement_ticket_quota: %s", e)
