import sqlite3
from datetime import datetime, timedelta

DB_FILE = "database.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        match_id INTEGER,
        created_at TEXT
    )""")
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users(user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def add_ticket(user_id, match_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tickets(user_id, match_id, created_at) VALUES (?, ?, ?)",
        (user_id, match_id, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_user_tickets(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def can_create_prediction(user_id, max_per_day=5):
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.utcnow().date()
    start_day = datetime.combine(today, datetime.min.time())
    end_day = datetime.combine(today, datetime.max.time())
    cursor.execute("""
        SELECT COUNT(*) as count FROM tickets
        WHERE user_id = ? AND created_at BETWEEN ? AND ?
    """, (user_id, start_day.isoformat(), end_day.isoformat()))
    count = cursor.fetchone()["count"]
    conn.close()
    return count < max_per_day
