import sqlite3
import logging
import json
from datetime import datetime, date

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
            plan TEXT DEFAULT 'free',         -- free / vip / pay_per_ticket
            ticket_balance INTEGER DEFAULT 0, -- solo per pay_per_ticket
            categories TEXT,                  -- JSON array di categorie preferite
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Tabella tickets
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            data TEXT,        -- JSON {"predictions": [...]}
            category TEXT,
            vip_only INTEGER DEFAULT 0,
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
        cur.execute("SELECT id, username, plan, ticket_balance, categories FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "id": row[0],
            "username": row[1],
            "plan": row[2],
            "ticket_balance": row[3],
            "categories": json.loads(row[4]) if row[4] else []
        }
    except Exception as e:
        logger.exception("Errore get_user: %s", e)
        return None

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

def set_plan(user_id, plan, add_tickets=0, categories=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        # Recupera ticket_balance corrente
        cur.execute("SELECT ticket_balance FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        current_balance = row[0] if row else 0
        new_balance = max(0, current_balance + add_tickets)

        # Aggiorna
        cats_json = json.dumps(categories) if categories is not None else None
        if cats_json:
            cur.execute("UPDATE users SET plan=?, ticket_balance=?, categories=? WHERE id=?", (plan, new_balance, cats_json, user_id))
        else:
            cur.execute("UPDATE users SET plan=?, ticket_balance=? WHERE id=?", (plan, new_balance, user_id))
        conn.commit()
        conn.close()
        logger.info("Utente %s aggiornato: plan=%s, ticket_balance=%s", user_id, plan, new_balance)
    except Exception as e:
        logger.exception("Errore set_plan: %s", e)

def add_tickets(user_id, num):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("UPDATE users SET ticket_balance = ticket_balance + ? WHERE id=?", (num, user_id))
        conn.commit()
        conn.close()
        logger.info("Aggiunti %d ticket a utente %s", num, user_id)
    except Exception as e:
        logger.exception("Errore add_tickets: %s", e)

def is_vip_user(user_id):
    user = get_user(user_id)
    return user and user["plan"] == "vip"

# =========================
# Gestione tickets
# =========================
def add_ticket(user_id, predictions, category="Generica", vip_only=0):
    try:
        normalized = {"predictions": predictions}
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("INSERT INTO tickets (user_id, data, category, vip_only) VALUES (?, ?, ?, ?)",
                    (user_id, json.dumps(normalized), category, vip_only))
        conn.commit()
        conn.close()
        logger.info("Ticket aggiunto per utente %s, category=%s, vip_only=%s", user_id, category, vip_only)
    except Exception as e:
        logger.exception("Errore add_ticket: %s", e)

def get_user_tickets(user_id, date_filter=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        if date_filter:
            cur.execute(
                "SELECT data, category, vip_only, created_at FROM tickets WHERE user_id=? AND date(created_at)=? ORDER BY created_at DESC",
                (user_id, date_filter)
            )
        else:
            cur.execute(
                "SELECT data, category, vip_only, created_at FROM tickets WHERE user_id=? ORDER BY created_at DESC",
                (user_id,)
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
                "category": row[1],
                "vip_only": row[2],
                "created_at": row[3]
            })
        return tickets
    except Exception as e:
        logger.exception("Errore get_user_tickets: %s", e)
        return []

def mark_ticket_used(user_id, ticket_id):
    # Opzionale: aggiungere flag "used" se necessario
    pass
