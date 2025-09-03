import sqlite3

conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    plan TEXT DEFAULT 'free',
    pronostici INT DEFAULT 0
)
""")
conn.commit()

def add_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def update_plan(user_id, plan, pronostici):
    cursor.execute("UPDATE users SET plan=?, pronostici=? WHERE user_id=?", (plan, pronostici, user_id))
    conn.commit()

def decrement_pronostico(user_id):
    cursor.execute("UPDATE users SET pronostici = pronostici - 1 WHERE user_id=?", (user_id,))
    conn.commit()
