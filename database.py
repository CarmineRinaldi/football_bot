import aiosqlite
import asyncio

DB_FILE = 'users.db'

# -------------------------------
# Creazione tabelle async
# -------------------------------
async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            plan TEXT DEFAULT 'free',
            pronostici INTEGER DEFAULT 0,
            started BOOLEAN DEFAULT 0
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS schedine (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            campionato TEXT,
            pronostico TEXT,
            data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """)
        await db.commit()

# -------------------------------
# Funzioni utenti async
# -------------------------------
async def add_user(user_id: int):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, started) VALUES (?, 0)",
            (user_id,)
        )
        await db.commit()

async def has_started(user_id: int) -> bool:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT started FROM users WHERE user_id=?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return bool(row["started"]) if row else False

async def mark_started(user_id: int):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("UPDATE users SET started=1 WHERE user_id=?", (user_id,))
        await db.commit()

async def get_user(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def update_plan(user_id: int, plan: str, pronostici: int):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "UPDATE users SET plan=?, pronostici=? WHERE user_id=?",
            (plan, pronostici, user_id)
        )
        await db.commit()

async def decrement_pronostico(user_id: int):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "UPDATE users SET pronostici = CASE WHEN pronostici>0 THEN pronostici-1 ELSE 0 END WHERE user_id=?",
            (user_id,)
        )
        await db.commit()

async def add_pronostici(user_id: int, amount: int):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "UPDATE users SET pronostici = pronostici + ? WHERE user_id=?",
            (amount, user_id)
        )
        await db.commit()

# -------------------------------
# Funzioni schedine async
# -------------------------------
async def add_schedina(user_id: int, campionato: str, pronostico: str):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT INTO schedine (user_id, campionato, pronostico) VALUES (?, ?, ?)",
            (user_id, campionato, pronostico)
        )
        await db.commit()

async def get_schedine(user_id: int, limit: int = 10) -> list[tuple]:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT campionato, pronostico, data_creazione FROM schedine WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [(r["campionato"], r["pronostico"], r["data_creazione"]) for r in rows]

# -------------------------------
# Inizializza DB all'avvio
# -------------------------------
asyncio.run(init_db())
