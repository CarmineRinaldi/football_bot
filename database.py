import sqlite3
from datetime import datetime, timedelta
from config import DATABASE_URL

def init_db():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    telegram_id INTEGER UNIQUE,
                    is_vip INTEGER DEFAULT 0,
                    last_free TIMESTAMP
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS schedine (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    match TEXT,
                    created_at TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )''')
    conn.commit()
    conn.close()

def add_user(telegram_id):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (telegram_id) VALUES (?)", (telegram_id,))
    conn.commit()
    conn.close()

def add_schedina(user_id, match):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("INSERT INTO schedine (user_id, match, created_at) VALUES (?, ?, ?)",
              (user_id, match, datetime.now()))
    conn.commit()
    conn.close()

def get_schedine(user_id):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    limit_time = datetime.now() - timedelta(hours=48)
    c.execute("SELECT match FROM schedine WHERE user_id=? AND created_at>=?", (user_id, limit_time))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_user(telegram_id):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,))
    user = c.fetchone()
    conn.close()
    return user

def update_last_free(user_id):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("UPDATE users SET last_free=? WHERE id=?", (datetime.now(), user_id))
    conn.commit()
    conn.close()

def cleanup_schedine():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    limit_time = datetime.now() - timedelta(hours=48)
    c.execute("DELETE FROM schedine WHERE created_at<?", (limit_time,))
    conn.commit()
    conn.close()
