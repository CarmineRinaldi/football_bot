import aiosqlite
from datetime import datetime, timedelta
from config import DATABASE_URL

async def init_db():
    async with aiosqlite.connect(DATABASE_URL) as conn:
        await conn.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY,
                                telegram_id INTEGER UNIQUE,
                                is_vip INTEGER DEFAULT 0,
                                last_free TIMESTAMP
                            )''')
        await conn.execute('''CREATE TABLE IF NOT EXISTS schedine (
                                id INTEGER PRIMARY KEY,
                                user_id INTEGER,
                                match TEXT,
                                created_at TIMESTAMP,
                                FOREIGN KEY(user_id) REFERENCES users(id)
                            )''')
        await conn.commit()

async def add_user(telegram_id):
    async with aiosqlite.connect(DATABASE_URL) as conn:
        await conn.execute("INSERT OR IGNORE INTO users (telegram_id) VALUES (?)", (telegram_id,))
        await conn.commit()

async def add_schedina(user_id, match):
    async with aiosqlite.connect(DATABASE_URL) as conn:
        await conn.execute(
            "INSERT INTO schedine (user_id, match, created_at) VALUES (?, ?, ?)",
            (user_id, match, datetime.now())
        )
        await conn.commit()

async def get_schedine(user_id):
    async with aiosqlite.connect(DATABASE_URL) as conn:
        limit_time = datetime.now() - timedelta(hours=48)
        async with conn.execute(
            "SELECT match FROM schedine WHERE user_id=? AND created_at>=?",
            (user_id, limit_time)
        ) as cursor:
            rows = await cursor.fetchall()
            return [r[0] for r in rows]

async def cleanup_schedine():
    async with aiosqlite.connect(DATABASE_URL) as conn:
        limit_time = datetime.now() - timedelta(hours=48)
        await conn.execute("DELETE FROM schedine WHERE created_at<?", (limit_time,))
        await conn.commit()
