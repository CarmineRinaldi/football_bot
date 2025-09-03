import sqlite3
import os
import json
from datetime import datetime, date

DB_FILE = os.environ.get("DB_FILE", "football_bot.db")

# =========================
# Inizializzazione DB
# =========================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Tabella utenti
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            plan TEXT DEFAULT 'free',
            ticket_quota INTEGER DEFAULT 0,
            categories TEXT DEFAULT ''
        )
    ''')
    # Tabella tickets
    c.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            predictions TEXT,
            vip_only INTEGER DEFAULT 0,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')
    conn.commit()
    conn.close()

# =========================
# Funzioni utenti
# =========================
def add_user(user_id, username=""):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users(user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

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
            "categories": row[4].split(",") if row[4] else []
        }
    return None

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def set_user_plan(user_id, plan, ticket_quota=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if ticket_quota is not None:
        c.execute("UPDATE users SET plan=?, ticket_quota=? WHERE user_id=?", (plan, ticket_quota, user_id))
    else:
        c.execute("UPDATE users SET plan=? WHERE user_id=?", (plan, user_id))
    conn.commit()
    conn.close()

def set_user_categories(user_id, categories):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    cat_str = ",".join(categories)
    c.execute("UPDATE users SET categories=? WHERE user_id=?", (cat_str, user_id))
    conn.commit()
    conn.close()

def increment_user_tickets(user_id, n):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET ticket_quota = ticket_quota + ? WHERE user_id=?", (n, user_id))
    conn.commit()
    conn.close()

# =========================
# Funzioni tickets
# =========================
def add_ticket(user_id, ticket):
    """ticket = {'category':..., 'predictions':[...], 'vip_only':0/1}"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO tickets (user_id, category, predictions, vip_only, created_at) VALUES (?, ?, ?, ?, ?)",
        (
            user_id,
            ticket.get("category", "N/A"),
            json.dumps(ticket.get("predictions", [])),
            ticket.get("vip_only", 0),
            date.today().isoformat()
        )
    )
    conn.commit()
    conn.close()

def get_user_tickets(user_id, date_filter=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if date_filter:
        c.execute("SELECT category, predictions, vip_only FROM tickets WHERE user_id=? AND created_at=?", (user_id, date_filter))
    else:
        c.execute("SELECT category, predictions, vip_only FROM tickets WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    tickets = []
    for r in rows:
        tickets.append({
            "category": r[0],
            "predictions": json.loads(r[1]),
            "vip_only": bool(r[2])
        })
    return tickets

def decrement_ticket_quota(user_id, n=1):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET ticket_quota = ticket_quota - ? WHERE user_id=? AND ticket_quota > 0", (n, user_id))
    conn.commit()
    conn.close()
