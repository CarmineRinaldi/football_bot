# db.py
import sqlite3
import os

# Percorso del database (di default users.db, oppure preso da variabile ambiente)
DB_FILE = os.environ.get("DB_FILE", "users.db")

def init_db():
    """Crea la tabella users se non esiste già."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    is_vip INTEGER DEFAULT 0
                )''')
    conn.commit()
    conn.close()

def add_user(user_id, username):
    """Aggiunge un nuovo utente al DB (se non esiste già)."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def set_vip(user_id, vip=1):
    """Imposta un utente come VIP (1) o non VIP (0)."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET is_vip=? WHERE user_id=?", (vip, user_id))
    conn.commit()
    conn.close()

def get_all_users():
    """Ritorna la lista di tutti gli user_id registrati."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]
