# db.py
import sqlite3
import os
import json
from datetime import date

DB_FILE = os.environ.get("DB_FILE", "users.db")

# -------------------------
# Init DB
# -------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Tabella utenti
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            plan TEXT DEFAULT 'free',    -- free / vip / pay
            vip INTEGER DEFAULT 0,
            ticket_quota INTEGER DEFAULT 0,
            categories TEXT DEFAULT '["Premier League"]'
        )
    ''')
    
    # Tabella tickets
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

# -------------------------
# Gestione utenti
# -------------------------
def add_user(user_id, username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id, username, plan, vip, ticket_quota, categories FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "user_id": row[0],
            "username": row[1],
            "plan": row[2],
            "vip": bool(row[3]),
            "ticket_quota": row[4],
            "categories": json.loads(row[5]) if row[5] else ["Premier League"]
        }
    return None

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

# -------------------------
# Piani e VIP
# -------------------------
def set_vip(user_id, value=True):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET vip=?, plan=? WHERE user_id=?", (int(value), "vip" if value else "free", user_id))
    conn.commit()
    conn.close()

def is_vip_user(user_id):
    user = get_user(user_id)
    return user.get("vip", False) if user else False

def set_plan(user_id, plan, ticket_quota=0):
    """Imposta il piano e eventualmente la quota ticket (per pay)"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET plan=?, ticket_quota=? WHERE user_id=?", (plan, ticket_quota, user_id))
    conn.commit()
    conn.close()

# -------------------------
# Categorie utente
# -------------------------
def set_user_categories(user_id, categories):
    """Imposta le categorie preferite dell'utente."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET categories=? WHERE user_id=?", (json.dumps(categories), user_id))
    conn.commit()
    conn.close()

def get_user_categories(user_id):
    """Recupera le categorie preferite dell'utente."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT categories FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        return json.loads(row[0])
    return ["Premier League"]

# -------------------------
# Ticket
# -------------------------
def add_ticket(user_id, ticket):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO tickets (user_id, pronostici, vip_only, created_at) VALUES (?, ?, ?, ?)",
        (user_id, json.dumps(ticket.get("predictions", [])), int(ticket.get("vip_only", 0)), date.today().isoformat())
    )
    conn.commit()
    conn.close()

def get_user_tickets(user_id, created_at=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if created_at:
        c.execute("SELECT ticket_id, pronostici, vip_only, created_at FROM tickets WHERE user_id=? AND created_at=? ORDER BY ticket_id ASC", (user_id, created_at))
    else:
        c.execute("SELECT ticket_id, pronostici, vip_only, created_at FROM tickets WHERE user_id=? ORDER BY ticket_id ASC", (user_id,))
    rows = c.fetchall()
    conn.close()
    tickets = []
    for r in rows:
        tickets.append({
            "ticket_id": r[0],
            "predictions": json.loads(r[1]),
            "vip_only": bool(r[2]),
            "created_at": r[3]
        })
    return tickets

def decrement_ticket_quota(user_id, amount=1):
    """Riduce la quota ticket del piano pay."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET ticket_quota = ticket_quota - ? WHERE user_id=? AND ticket_quota >= ?", (amount, user_id, amount))
    conn.commit()
    conn.close()
