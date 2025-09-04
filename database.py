import sqlite3
import threading

# -------------------------------
# Connessione al database SQLite
# -------------------------------
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# Lock per accesso thread-safe al database
db_lock = threading.Lock()

# -------------------------------
# Creazione della tabella utenti
# -------------------------------
with db_lock:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        plan TEXT DEFAULT 'free',
        pronostici INT DEFAULT 0,
        started BOOLEAN DEFAULT 0
    )
    """)
    conn.commit()

# -------------------------------
# Funzioni per gestire gli utenti
# -------------------------------

def add_user(user_id):
    """Aggiunge un utente se non esiste ancora."""
    with db_lock:
        cursor.execute("INSERT OR IGNORE INTO users (user_id, started) VALUES (?, 0)", (user_id,))
        conn.commit()

def has_started(user_id):
    """Verifica se l'utente ha già cliccato /start."""
    with db_lock:
        cursor.execute("SELECT started FROM users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        return bool(result[0]) if result else False

def mark_started(user_id):
    """Segna che l'utente ha già cliccato /start."""
    with db_lock:
        cursor.execute("UPDATE users SET started=1 WHERE user_id=?", (user_id,))
        conn.commit()

def get_user(user_id):
    """Restituisce tutti i dati dell'utente."""
    with db_lock:
        cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return cursor.fetchone()

def update_plan(user_id, plan, pronostici):
    """Aggiorna il piano e i pronostici dell'utente."""
    with db_lock:
        cursor.execute("UPDATE users SET plan=?, pronostici=? WHERE user_id=?", (plan, pronostici, user_id))
        conn.commit()

def decrement_pronostico(user_id):
    """Decrementa di 1 i pronostici dell'utente."""
    with db_lock:
        cursor.execute("UPDATE users SET pronostici = pronostici - 1 WHERE user_id=? AND pronostici > 0", (user_id,))
        conn.commit()

def add_pronostici(user_id, amount):
    """Aggiunge un numero di pronostici all'utente."""
    with db_lock:
        cursor.execute("UPDATE users SET pronostici = pronostici + ? WHERE user_id=?", (amount, user_id))
        conn.commit()
