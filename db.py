import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.environ.get("DATABASE_URL", "users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            plan TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS schedine (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            matches TEXT,
            odds TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_id, username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (id, username, plan) VALUES (?, ?, ?)", (user_id, username, "free"))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "plan": row[2]}
    return None

def update_user_plan(user_id, plan):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET plan=? WHERE id=?", (plan, user_id))
    conn.commit()
    conn.close()

def add_schedina(user_id, matches, odds):
    import json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO schedine (user_id, matches, odds) VALUES (?, ?, ?)",
              (user_id, json.dumps(matches), json.dumps(odds)))
    conn.commit()
    conn.close()

def get_schedine(user_id):
    import json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    limit_date = datetime.now() - timedelta(days=10)
    c.execute("DELETE FROM schedine WHERE created_at < ?", (limit_date,))
    conn.commit()
    c.execute("SELECT matches, odds FROM schedine WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    schedine = []
    for m, o in rows:
        schedine.append({"matches": json.loads(m), "odds": json.loads(o)})
    return schedine
