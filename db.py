import sqlite3
import time
import json

DB_FILE = "users.db"

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        plan TEXT,
        credits INTEGER DEFAULT 0,
        vip_until INTEGER DEFAULT 0
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS schedine (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        created_at INTEGER,
        matches TEXT,
        odds TEXT
    )""")
    conn.commit()
    conn.close()

def add_user(user_id, username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None

def update_user_plan(user_id, plan, credits=0, vip_until=0):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET plan=?, credits=?, vip_until=? WHERE id=?", (plan, credits, vip_until, user_id))
    conn.commit()
    conn.close()

def add_schedina(user_id, matches, odds):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO schedine (user_id, created_at, matches, odds) VALUES (?, ?, ?, ?)",
              (user_id, int(time.time()), json.dumps(matches), json.dumps(odds)))
    conn.commit()
    conn.close()

def get_schedine(user_id):
    conn = get_conn()
    c = conn.cursor()
    ten_days_ago = int(time.time()) - 10*24*60*60
    c.execute("DELETE FROM schedine WHERE created_at < ?", (ten_days_ago,))
    conn.commit()
    c.execute("SELECT * FROM schedine WHERE user_id=?", (user_id,))
    schedine = c.fetchall()
    conn.close()
    result = []
    for s in schedine:
        result.append({
            "id": s["id"],
            "matches": json.loads(s["matches"]),
            "odds": json.loads(s["odds"])
        })
    return result
