import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional
from config import DATABASE_URL


def init_db() -> None:
    """Inizializza le tabelle nel database se non esistono già."""
    with sqlite3.connect(DATABASE_URL) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE,
                is_vip INTEGER DEFAULT 0,
                last_free TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS schedine (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                match TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        conn.commit()


def add_user(telegram_id: int) -> None:
    """Aggiunge un utente se non esiste già."""
    with sqlite3.connect(DATABASE_URL) as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (telegram_id) VALUES (?)", (telegram_id,))
        conn.commit()


def add_schedina(user_id: int, match: str) -> None:
    """Aggiunge una schedina per un utente."""
    with sqlite3.connect(DATABASE_URL) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO schedine (user_id, match, created_at) VALUES (?, ?, ?)",
            (user_id, match, datetime.utcnow())
        )
        conn.commit()


def get_schedine(user_id: int) -> List[str]:
    """Restituisce le schedine di un utente non più vecchie di 48 ore."""
    limit_time = datetime.utcnow() - timedelta(hours=48)
    with sqlite3.connect(DATABASE_URL) as conn:
        c = conn.cursor()
        c.execute(
            "SELECT match FROM schedine WHERE user_id=? AND created_at>=?",
            (user_id, limit_time)
        )
        rows = c.fetchall()
    return [r[0] for r in rows]


def cleanup_schedine() -> None:
    """Elimina schedine più vecchie di 48 ore."""
    limit_time = datetime.utcnow() - timedelta(hours=48)
    with sqlite3.connect(DATABASE_URL) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM schedine WHERE created_at<?", (limit_time,))
        conn.commit()
