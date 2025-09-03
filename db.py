import os
import sqlite3
from datetime import date

DB_FILE = os.environ.get("DB_FILE", "bot.db")

# ------------------------------
# DB connection helper
# ------------------------------
def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# ------------------------------
# Initialization
# ------------------------------
def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            plan TEXT DEFAULT 'free',
            ticket_quota INTEGER DEFAULT 0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            created_at TEXT,
            category TEXT,
            predictions TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_categories (
            user_id INTEGER PRIMARY KEY,
            categories TEXT
        )
    """)
    conn.commit()
    conn.close()

# ------------------------------
# User management
# ------------------------------
def add_user(user_id, username="", first_name=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
              (user_id, username, first_name))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def set_user_plan(user_id, plan, ticket_quota=0):
    """Imposta il piano dell'utente e quota ticket (per pay/vip)"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO users (user_id, plan, ticket_quota)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET plan=excluded.plan, ticket_quota=excluded.ticket_quota
    """, (user_id, plan, ticket_quota))
    conn.commit()
    conn.close()

def decrement_ticket_quota(user_id, n=1):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET ticket_quota = ticket_quota - ? WHERE user_id=? AND ticket_quota>=?", (n, user_id, n))
    conn.commit()
    conn.close()

# ------------------------------
# Tickets management
# ------------------------------
def add_ticket(user_id, ticket):
    conn = get_conn()
    c = conn.cursor()
    today = str(date.today())
    predictions_str = "\n".join(ticket.get("predictions", []))
    c.execute("INSERT INTO tickets (user_id, created_at, category, predictions) VALUES (?, ?, ?, ?)",
              (user_id, today, ticket.get("category"), predictions_str))
    conn.commit()
    conn.close()

def get_user_tickets(user_id, created_at=None):
    conn = get_conn()
    c = conn.cursor()
    if created_at:
        c.execute("SELECT * FROM tickets WHERE user_id=? AND created_at=?", (user_id, created_at))
    else:
        c.execute("SELECT * FROM tickets WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    tickets = []
    for row in rows:
        tickets.append({
            "id": row["id"],
            "user_id": row["user_id"],
            "created_at": row["created_at"],
            "category": row["category"],
            "predictions": row["predictions"].split("\n")
        })
    return tickets

# ------------------------------
# User categories
# ------------------------------
def set_user_categories(user_id, categories):
    conn = get_conn()
    c = conn.cursor()
    categories_str = ",".join(categories)
    c.execute("""
        INSERT INTO user_categories (user_id, categories)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET categories=excluded.categories
    """, (user_id, categories_str))
    conn.commit()
    conn.close()

def get_user_categories(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT categories FROM user_categories WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row and row["categories"]:
        return row["categories"].split(",")
    return []

# ------------------------------
# VIP management
# ------------------------------
def is_vip_user(user_id):
    user = get_user(user_id)
    if user:
        return user.get("plan") in ("vip", "pay")
    return False
