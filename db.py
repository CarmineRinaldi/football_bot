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
            plan TEXT DEFAULT 'free',          -- free, vip, pay
            quota INTEGER DEFAULT 0,           -- solo per pay
            categories TEXT DEFAULT '["Premier League"]',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            vip INTEGER DEFAULT 0
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

def get_user(user_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT id, username, plan, quota, categories, vip FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return {}
        return {
            "id": row[0],
            "username": row[1],
            "plan": row[2],
            "quota": row[3],
            "categories": json.loads(row[4]),
            "vip": bool(row[5])
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

# =========================
# Piani e categorie
# =========================
def set_plan(user_id, plan="free", quota=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        if quota is not None:
            cur.execute("UPDATE users SET plan=?, quota=? WHERE id=?", (plan, quota, user_id))
        else:
            cur.execute("UPDATE users SET plan=? WHERE id=?", (plan, user_id))
        conn.commit()
        conn.close()
        logger.info("Utente %s impostato piano %s con quota=%s", user_id, plan, quota)
    except Exception as e:
        logger.exception("Errore set_plan: %s", e)

def set_user_categories(user_id, categories):
    """categories = lista di stringhe"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("UPDATE users SET categories=? WHERE id=?", (json.dumps(categories), user_id))
        conn.commit()
        conn.close()
        logger.info("Utente %s aggiornato categorie: %s", user_id, categories)
    except Exception as e:
        logger.exception("Errore set_user_categories: %s", e)

def decrement_ticket_quota(user_id, amount=1):
    """Riduce la quota di ticket disponibili per piano pay."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("UPDATE users SET quota = quota - ? WHERE id=?", (amount, user_id))
        conn.commit()
        conn.close()
        logger.info("Utente %s ridotta quota di %s", user_id, amount)
    except Exception as e:
        logger.exception("Errore decrement_ticket_quota: %s", e)

# =========================
# Gestione tickets
# =========================
def add_ticket(user_id, ticket_data):
    try:
        normalized = {"predictions": ticket_data.get("predictions", []), "category": ticket_data.get("category")}
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
                "category": data.get("category", "N/A"),
                "created_at": row[1]
            })
        return tickets
    except Exception as e:
        logger.exception("Errore get_user_tickets: %s", e)
        return []
