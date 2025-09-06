import sqlite3
from datetime import date

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

# --- Tabelle esistenti ---
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    plan TEXT DEFAULT 'free'
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    match_ids TEXT,
    date_created TEXT
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS predictions (
    user_id INTEGER,
    match_id INTEGER,
    prediction TEXT,
    date_created TEXT
)""")

# --- Tabella limit giornaliero ---
cursor.execute("""CREATE TABLE IF NOT EXISTS daily_limit (
    user_id INTEGER PRIMARY KEY,
    date TEXT,
    count INTEGER
)""")
conn.commit()

def add_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def get_user_plan(user_id):
    cursor.execute("SELECT plan FROM users WHERE user_id=?", (user_id,))
    res = cursor.fetchone()
    return res[0] if res else "free"

def can_create_prediction(user_id):
    today = str(date.today())
    cursor.execute("SELECT count FROM daily_limit WHERE user_id=? AND date=?", (user_id, today))
    res = cursor.fetchone()
    if res and res[0] >= 5:
        return False
    return True

def increment_prediction_count(user_id):
    today = str(date.today())
    cursor.execute("SELECT count FROM daily_limit WHERE user_id=? AND date=?", (user_id, today))
    res = cursor.fetchone()
    if res:
        cursor.execute("UPDATE daily_limit SET count = count + 1 WHERE user_id=? AND date=?", (user_id, today))
    else:
        cursor.execute("INSERT INTO daily_limit (user_id, date, count) VALUES (?, ?, 1)", (user_id, today))
    conn.commit()

def add_match_prediction(user_id, match_id, prediction):
    if not can_create_prediction(user_id):
        return False
    cursor.execute("INSERT INTO predictions (user_id, match_id, prediction, date_created) VALUES (?, ?, ?, ?)",
                   (user_id, match_id, prediction, str(date.today())))
    increment_prediction_count(user_id)
    conn.commit()
    return True

def get_user_tickets(user_id):
    cursor.execute("SELECT match_ids, date_created FROM tickets WHERE user_id=?", (user_id,))
    return [{"match_ids": r[0], "date_created": r[1]} for r in cursor.fetchall()]

def add_ticket(user_id, match_ids):
    cursor.execute("INSERT INTO tickets (user_id, match_ids, date_created) VALUES (?, ?, ?)",
                   (user_id, ",".join(map(str, match_ids)), str(date.today())))
    conn.commit()
