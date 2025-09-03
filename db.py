import sqlite3
import os
import json
from datetime import date

DB_FILE = os.environ.get("DB_FILE", "users.db")  # stesso DB di users

# =========================
# UTENTI
# =========================
def init_db():
    """Crea le tabelle users e tickets se non esistono."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Tabella utenti
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            plan TEXT DEFAULT 'free',
            ticket_quota INTEGER DEFAULT 0,
            categories TEXT
        )
    ''')
    conn.commit()
    conn.close()
    init_tickets_db()

def add_user(user_id, username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO users (user_id, username, categories) VALUES (?, ?, ?)",
        (user_id, username, json.dumps([]))
    )
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id, username, plan, ticket_quota, categories FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "user_id": row[0],
            "username": row[1],
            "plan": row[2],
            "ticket_quota": row[3],
            "categories": json.loads(row[4] or "[]")
        }
    return None

def set_user_plan(user_id, plan):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET plan=? WHERE user_id=?", (plan, user_id))
    conn.commit()
    conn.close()

def set_user_categories(user_id, categories):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET categories=? WHERE user_id=?", (json.dumps(categories), user_id))
    conn.commit()
    conn.close()

# =========================
# TICKET
# =========================
def init_tickets_db():
    """Crea la tabella tickets se non esiste."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            pronostici TEXT,
            vip_only INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def create_ticket(user_id, pronostici, vip_only=0):
    """Salva una schedina per un utente."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO tickets (user_id, pronostici, vip_only, created_at) VALUES (?, ?, ?, ?)",
        (user_id, json.dumps(pronostici), vip_only, date.today().isoformat())
    )
    conn.commit()
    conn.close()

def get_user_tickets(user_id, is_vip=0):
    """Recupera le schedine per l'utente (VIP o Free)."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if is_vip:
        c.execute(
            "SELECT ticket_id, pronostici FROM tickets WHERE user_id=? ORDER BY ticket_id DESC",
            (user_id,)
        )
    else:
        # solo schedine non VIP, max 10
        c.execute(
            "SELECT ticket_id, pronostici FROM tickets WHERE user_id=? AND vip_only=0 ORDER BY ticket_id DESC LIMIT 10",
            (user_id,)
        )
    rows = c.fetchall()
    conn.close()
    tickets = []
    for r in rows:
        tickets.append({
            "ticket_id": r[0],
            "pronostici": json.loads(r[1])
        })
    return tickets

def delete_old_tickets():
    """Opzionale: pulisce schedine di giorni precedenti."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    today = date.today().isoformat()
    c.execute("DELETE FROM tickets WHERE created_at<>?", (today,))
    conn.commit()
    conn.close()

# =========================
# GESTIONE TICKET PAY
# =========================
def decrement_ticket_quota(user_id, amount=1):
    """Diminuisce la quota di ticket per un utente pay."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET ticket_quota = ticket_quota - ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

def increment_user_tickets(user_id, amount=10):
    """Aumenta la quota di ticket per un utente pay."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET ticket_quota = ticket_quota + ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()
