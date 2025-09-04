import sqlite3
import threading

DB_FILE = 'users.db'
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()
db_lock = threading.Lock()

# Creazione tabelle
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    started INTEGER DEFAULT 0,
    pronostici_free INTEGER DEFAULT 5
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS schedine (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    campionato TEXT,
    schedina TEXT
)
""")
conn.commit()

# ----------------- Funzioni database -----------------
async def add_user(user_id):
    with db_lock:
        cursor.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (user_id,))
        conn.commit()

async def has_started(user_id):
    with db_lock:
        cursor.execute("SELECT started FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        return row and row[0] == 1

async def mark_started(user_id):
    with db_lock:
        cursor.execute("UPDATE users SET started=1 WHERE user_id=?", (user_id,))
        conn.commit()

async def decrement_pronostico(user_id):
    with db_lock:
        cursor.execute("UPDATE users SET pronostici_free = pronostici_free - 1 WHERE user_id=? AND pronostici_free>0", (user_id,))
        conn.commit()

async def get_schedine(user_id):
    with db_lock:
        cursor.execute("SELECT id, schedina FROM schedine WHERE user_id=?", (user_id,))
        return cursor.fetchall()

async def add_schedina(user_id, campionato, schedina):
    with db_lock:
        cursor.execute("INSERT INTO schedine(user_id, campionato, schedina) VALUES(?,?,?)",
                       (user_id, campionato, schedina))
        conn.commit()
