import sqlite3
import os
from datetime import datetime

DB_FILE = os.environ.get("DB_FILE", "/tmp/users.db")

def get_conn():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# =========================
# Inizializzazione DB
# =========================
def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            plan TEXT DEFAULT 'free',
            ticket_quota INTEGER DEFAULT 0,
            categories TEXT DEFAULT ''
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            predictions TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    conn.commit()
    conn.close()

# =========================
# Funzioni utenti
# =========================
def add_user(user_id, username):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "user_id": row["user_id"],
        "username": row["username"],
        "plan": row["plan"],
        "ticket_quota": row["ticket_quota"],
        "categories": row["categories"].split(",") if row["categories"] else []
    }

def get_all_users():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [r["user_id"] for r in rows]

def set_user_plan(user_id, plan):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET plan=? WHERE user_id=?", (plan, user_id))
    conn.commit()
    conn.close()

def set_user_categories(user_id, categories):
    conn = get_conn()
    cursor = conn.cursor()
    cats_str = ",".join(categories)
    cursor.execute("UPDATE users SET categories=? WHERE user_id=?", (cats_str, user_id))
    conn.commit()
    conn.close()

# =========================
# Ticket
# =========================
def get_user_tickets(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    tickets = []
    for r in rows:
        tickets.append({
            "id": r["id"],
            "category": r["category"],
            "predictions": r["predictions"].split(",") if r["predictions"] else [],
            "created_at": r["created_at"]
        })
    return tickets

def add_ticket(user_id, category, predictions):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tickets (user_id, category, predictions, created_at) VALUES (?, ?, ?, ?)",
        (user_id, category, ",".join(predictions), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def decrement_ticket_quota(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET ticket_quota = ticket_quota - 1 WHERE user_id=? AND ticket_quota > 0", (user_id,))
    conn.commit()
    conn.close()
