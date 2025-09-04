import sqlite3
import threading

# -------------------------------
# Connessione al database SQLite
# -------------------------------
DB_FILE = 'users.db'  # puoi anche usare os.environ.get("DB_FILE")
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
conn.row_factory = sqlite3.Row  # rende i risultati come dizionari
cursor = conn.cursor()

# Lock per accesso thread-safe al database
db_lock = threading.Lock()

# -------------------------------
# Creazione tabelle
# -------------------------------
with db_lock:
    # Tabella utenti
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        plan TEXT DEFAULT 'free',
        pronostici INT DEFAULT 0,
        started BOOLEAN DEFAULT 0
    )
    """)

    # Tabella schedine
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedine (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        campionato TEXT,
        pronostico TEXT,
        data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)
    conn.commit()

# -------------------------------
# Funzioni utenti
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
        return bool(result["started"]) if result else False

def mark_started(user_id):
    """Segna che l'utente ha già cliccato /start."""
    with db_lock:
        cursor.execute("UPDATE users SET started=1 WHERE user_id=?", (user_id,))
        conn.commit()

def get_user(user_id):
    """Restituisce tutti i dati dell'utente come dizionario."""
    with db_lock:
        cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_plan(user_id, plan, pronostici):
    """Aggiorna il piano e i pronostici dell'utente."""
    with db_lock:
        cursor.execute("UPDATE users SET plan=?, pronostici=? WHERE user_id=?", (plan, pronostici, user_id))
        conn.commit()

def decrement_pronostico(user_id):
    """Decrementa di 1 i pronostici dell'utente, evitando valori negativi."""
    with db_lock:
        cursor.execute("UPDATE users SET pronostici = CASE WHEN pronostici>0 THEN pronostici-1 ELSE 0 END WHERE user_id=?", (user_id,))
        conn.commit()

def add_pronostici(user_id, amount):
    """Aggiunge un numero di pronostici all'utente."""
    with db_lock:
        cursor.execute("UPDATE users SET pronostici = pronostici + ? WHERE user_id=?", (amount, user_id))
        conn.commit()

# -------------------------------
# Funzioni schedine
# -------------------------------

def add_schedina(user_id, campionato, pronostico):
    """Aggiunge una schedina per un utente."""
    with db_lock:
        cursor.execute(
            "INSERT INTO schedine (user_id, campionato, pronostico) VALUES (?, ?, ?)",
            (user_id, campionato, pronostico)
        )
        conn.commit()

def get_schedine(user_id, limit=10):
    """Recupera le ultime schedine salvate dall'utente."""
    with db_lock:
        cursor.execute(
            "SELECT campionato, pronostico, data_creazione FROM schedine WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        return [(r["campionato"], r["pronostico"], r["data_creazione"]) for r in rows]
