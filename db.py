import sqlite3
import os

DB_FILE = os.environ.get("DB_FILE", "users.db")

def init_db():
    """Crea le tabelle users e tickets se non esistono."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    is_vip INTEGER DEFAULT 0
                )''')
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

def add_user(user_id, username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def set_vip(user_id, vip=1):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET is_vip=? WHERE user_id=?", (vip, user_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def is_vip_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT is_vip FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return bool(row[0]) if row else False

