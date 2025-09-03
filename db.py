import sqlite3
import logging
import json
from datetime import datetime, date

logger = logging.getLogger(__name__)
DB_FILE = "bot.db"  # puoi usare os.environ.get("DB_FILE") se vuoi configurarlo esternamente

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
            plan TEXT DEFAULT 'free',  -- free, vip, pay
            ticket_quota INTEGER DEFAULT 0,  -- solo per piano pay
            categories TEXT DEFAULT '[]',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Tabella tickets
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            data TEXT,  -- {"predictions": [...], "category": "..."}
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
        cur.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)", (user_id, username))
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

def get_user(user_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT id, username, plan, ticket_quota, categories FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "id": row[0],
            "username": row[1],
            "plan": row[2],
            "ticket_quota": row[3],
            "categories": json.loads(row[4] or "[]")
        }
    except Exception as e:
        logger.exception("Errore get_user: %s", e)
        return None

def is_vip_user(user_id):
    user = get_user(user_id)
    return user and user.get("plan") == "vip"

def set_user_plan(user_id, plan, quota=0):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("UPDATE users SET plan=?, ticket_quota=? WHERE id=?", (plan, quota, user_id))
        conn.commit()
        conn.close()
        logger.info("Utente %s aggiornato plan=%s quota=%s", user_id, plan, quota)
    except Exception as e:
        logger.exception("Errore set_user_plan: %s", e)

# =========================
# Gestione ticket quota pay
# =========================
def decrement_ticket_quota(user_id, amount=1):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("UPDATE users SET ticket_quota = ticket_quota - ? WHERE id=? AND ticket_quota>=?", (amount, user_id, amount))
        conn.commit()
        conn.close()
        logger.info("Utente %s decrementata quota ticket di %s", user_id, amount)
    except Exception as e:
        logger.exception("Errore decrement_ticket_quota: %s", e)

# =========================
# Gestione tickets
# =========================
def add_ticket(user_id, ticket_data):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("INSERT INTO tickets (user_id, data) VALUES (?, ?)", (user_id, json.dumps(ticket_data)))
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
            cur.execute("SELECT data, created_at FROM tickets WHERE user_id=? AND date(created_at)=? ORDER BY created_at DESC", (user_id, date_filter))
        else:
            cur.execute("SELECT data, created_at FROM tickets WHERE user_id=? ORDER BY created_at DESC", (user_id,))
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
                "category": data.get("category"),
                "created_at": row[1]
            })
        return tickets
    except Exception as e:
        logger.exception("Errore get_user_tickets: %s", e)
        return []

