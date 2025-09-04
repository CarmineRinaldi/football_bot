import sqlite3
import threading
from datetime import datetime, timedelta

DB_FILE = 'users.db'
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()
db_lock = threading.Lock()

# Creazione tabelle
with db_lock:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        started INTEGER DEFAULT 0
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedine (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        pronostico TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

# Funzioni database
def add_user(user_id, username):
    with db_lock:
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()

def has_started(user_id):
    with db_lock:
        cursor.execute("SELECT started FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        return bool(row[0]) if row else False

def mark_started(user_id):
    with db_lock:
        cursor.execute("UPDATE users SET started=1 WHERE user_id=?", (user_id,))
        conn.commit()

def add_pronostico(user_id, pronostico):
    with db_lock:
        cursor.execute("INSERT INTO schedine (user_id, pronostico) VALUES (?, ?)", (user_id, pronostico))
        conn.commit()

def get_schedine(user_id):
    with db_lock:
        ten_days_ago = datetime.now() - timedelta(days=10)
        cursor.execute("""
            SELECT pronostico, created_at 
            FROM schedine 
            WHERE user_id=? AND created_at >= ?
            ORDER BY created_at DESC
        """, (user_id, ten_days_ago))
        return cursor.fetchall()

def decrement_pronostico(user_id):
    # Se serve logica aggiuntiva per decrementare, qui puoi aggiungerla
    pass

def cleanup_schedine():
    # Rimuove schedine più vecchie di 10 giorni
    with db_lock:
        ten_days_ago = datetime.now() - timedelta(days=10)
        cursor.execute("DELETE FROM schedine WHERE created_at < ?", (ten_days_ago,))
        conn.commit()
