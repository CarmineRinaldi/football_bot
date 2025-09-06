import sqlite3

DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        plan TEXT DEFAULT 'free',
        matches_used INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

def add_user(user_id: int, plan: str = "free"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (user_id, plan, matches_used) VALUES (?, ?, 0)", (user_id, plan))
    conn.commit()
    conn.close()

def get_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT plan, matches_used FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"plan": row[0], "matches_used": row[1]}
    return {"plan": "free", "matches_used": 0}

def update_matches(user_id: int, matches_used: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET matches_used = ? WHERE user_id = ?", (matches_used, user_id))
    conn.commit()
    conn.close()
