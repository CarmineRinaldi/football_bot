import sqlite3
import json
import logging
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)
DB_FILE = os.environ.get("DB_FILE", "bot.db")

# =========================
# Inizializzazione DB
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
            plan TEXT DEFAULT 'free',             -- free, vip, pay_per_ticket
            vip_expiry TEXT,                       -- per VIP mensile
            ticket_balance INTEGER DEFAULT 0,      -- per pacchetti pay-per-ticket
            categories TEXT DEFAULT '[]',          -- JSON array di categorie
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Tabella tickets
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            pronostici TEXT,      -- JSON array
            vip_only INTEGER DEFAULT 0,
            categoria TEXT,
            date TEXT,
            used INTEGER DEFAULT 0,
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

def get_user(user_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "id": row[0],
            "username": row[1],
            "plan": row[2],
            "vip_expiry": row[3],
            "ticket_balance": row[4],
            "categories": json.loads(row[5] or "[]"),
            "created_at": row[6]
        }
    except Exception as e:
        logger.exception("Errore get_user: %s", e)
        return None

def is_vip_user(user_id):
    user = get_user(user_id)
    if not user:
        return False
    if user["plan"] != "vip":
        return False
    # Controllo scadenza VIP
    if user["vip_expiry"]:
        expiry = datetime.fromisoformat(user["vip_expiry"])
        if expiry < datetime.now():
            # VIP scaduto, downgrade automatico
            set_plan(user_id, "free")
            return False
    return True

def set_plan(user_id, plan, vip_days=None, add_tickets=None):
    """Aggiorna piano utente: vip_days serve per VIP mensile, add_tickets per pacchetto."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        vip_expiry = None
        ticket_balance = None
        if plan == "vip" and vip_days:
            vip_expiry = (datetime.now() + timedelta(days=vip_days)).isoformat()
            cur.execute("""
                UPDATE users SET plan=?, vip_expiry=?, ticket_balance=0 WHERE id=?
            """, (plan, vip_expiry, user_id))
        elif plan == "pay_per_ticket" and add_tickets:
            # incrementa ticket_balance
            cur.execute("""
                UPDATE users SET plan=?, ticket_balance=ticket_balance + ? WHERE id=?
            """, (plan, add_tickets, user_id))
        else:
            # free o aggiornamento normale
            cur.execute("UPDATE users SET plan=? WHERE id=?", (plan, user_id))
        conn.commit()
        conn.close()
        logger.info("Utente %s aggiornato piano=%s", user_id, plan)
    except Exception as e:
        logger.exception("Errore set_plan: %s", e)

def set_user_categories(user_id, categories):
    """Aggiorna categorie preferite dell'utente (lista di stringhe)."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("UPDATE users SET categories=? WHERE id=?", (json.dumps(categories), user_id))
        conn.commit()
        conn.close()
        logger.info("Utente %s aggiornato categorie=%s", user_id, categories)
    except Exception as e:
        logger.exception("Errore set_user_categories: %s", e)

# =========================
# Gestione tickets
# =========================
def add_ticket(user_id, pronostici, categoria, vip_only=0):
    """Salva una schedina per un utente."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO tickets (user_id, pronostici, vip_only, categoria, date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, json.dumps(pronostici), vip_only, categoria, datetime.now().date().isoformat()))
        conn.commit()
        conn.close()
        logger.info("Ticket aggiunto per utente %s categoria %s", user_id, categoria)
    except Exception as e:
        logger.exception("Errore add_ticket: %s", e)

def get_user_tickets(user_id, categoria=None, unused_only=False):
    """Recupera ticket filtrando per categoria o stato."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        query = "SELECT id, pronostici, vip_only, categoria, date, used FROM tickets WHERE user_id=?"
        params = [user_id]
        if categoria:
            query += " AND categoria=?"
            params.append(categoria)
        if unused_only:
            query += " AND used=0"
        query += " ORDER BY id DESC"
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        tickets = []
        for r in rows:
            tickets.append({
                "id": r[0],
                "pronostici": json.loads(r[1]),
                "vip_only": bool(r[2]),
                "categoria": r[3],
                "date": r[4],
                "used": bool(r[5])
            })
        return tickets
    except Exception as e:
        logger.exception("Errore get_user_tickets: %s", e)
        return []

def mark_ticket_used(ticket_id):
    """Segna un ticket come usato."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("UPDATE tickets SET used=1 WHERE id=?", (ticket_id,))
        conn.commit()
        conn.close()
        logger.info("Ticket %s segnato come usato", ticket_id)
    except Exception as e:
        logger.exception("Errore mark_ticket_used: %s", e)
