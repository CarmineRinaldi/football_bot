from __future__ import annotations
import aiosqlite
import json
import time
from typing import Any, Dict, List, Optional
from .config import settings

_DB: Optional[aiosqlite.Connection] = None

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tg_user_id INTEGER UNIQUE NOT NULL,
  username TEXT,
  first_name TEXT,
  plan TEXT DEFAULT 'free', -- 'free' or 'vip'
  vip_until INTEGER DEFAULT 0, -- unix ts
  slip_credits INTEGER DEFAULT 0,
  created_at INTEGER DEFAULT (strftime('%s','now'))
);

CREATE TABLE IF NOT EXISTS drafts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tg_user_id INTEGER NOT NULL,
  items_json TEXT NOT NULL,
  created_at INTEGER DEFAULT (strftime('%s','now'))
);

CREATE TABLE IF NOT EXISTS slips (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tg_user_id INTEGER NOT NULL,
  items_json TEXT NOT NULL,
  combined_odds REAL NOT NULL,
  created_at INTEGER DEFAULT (strftime('%s','now')),
  expires_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS stripe_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tg_user_id INTEGER NOT NULL,
  session_id TEXT UNIQUE NOT NULL,
  mode TEXT NOT NULL, -- 'payment' or 'subscription'
  status TEXT DEFAULT 'open',
  created_at INTEGER DEFAULT (strftime('%s','now'))
);

CREATE INDEX IF NOT EXISTS idx_users_tg ON users(tg_user_id);
CREATE INDEX IF NOT EXISTS idx_slips_user ON slips(tg_user_id);
CREATE INDEX IF NOT EXISTS idx_slips_exp ON slips(expires_at);
"""

async def connect() -> aiosqlite.Connection:
    global _DB
    if _DB is None:
        _DB = await aiosqlite.connect(settings.DATABASE_URL)
        _DB.row_factory = aiosqlite.Row
        await _DB.executescript(SCHEMA_SQL)
        await _DB.commit()
    return _DB

async def close() -> None:
    global _DB
    if _DB is not None:
        await _DB.close()
        _DB = None

# --- Users ---
async def upsert_user(tg_user_id: int, username: Optional[str], first_name: Optional[str]) -> None:
    db = await connect()
    await db.execute(
        """
        INSERT INTO users (tg_user_id, username, first_name)
        VALUES (?, ?, ?)
        ON CONFLICT(tg_user_id) DO UPDATE SET
          username=excluded.username,
          first_name=excluded.first_name
        """, (tg_user_id, username, first_name))
    await db.commit()

async def get_user(tg_user_id: int):
    db = await connect()
    cur = await db.execute("SELECT * FROM users WHERE tg_user_id=?", (tg_user_id,))
    return await cur.fetchone()

async def set_vip(tg_user_id: int, until_ts: int) -> None:
    db = await connect()
    await db.execute("UPDATE users SET plan='vip', vip_until=? WHERE tg_user_id=?", (until_ts, tg_user_id))
    await db.commit()

async def ensure_free_if_expired(tg_user_id: int) -> None:
    db = await connect()
    now = int(time.time())
    await db.execute("UPDATE users SET plan='free' WHERE tg_user_id=? AND plan='vip' AND vip_until>0 AND vip_until<?",
                     (tg_user_id, now))
    await db.commit()

async def add_credits(tg_user_id: int, amount: int) -> None:
    db = await connect()
    await db.execute("UPDATE users SET slip_credits = COALESCE(slip_credits,0) + ? WHERE tg_user_id=?",
                     (amount, tg_user_id))
    await db.commit()

async def consume_credit_if_needed(tg_user_id: int) -> bool:
    row = await get_user(tg_user_id)
    if row is None:
        return False
    # VIP?
    await ensure_free_if_expired(tg_user_id)
    row = await get_user(tg_user_id)
    if row and row["plan"] == "vip":
        return True
    # Non-VIP ⇒ serve credito
    db = await connect()
    cur = await db.execute("SELECT slip_credits FROM users WHERE tg_user_id=?", (tg_user_id,))
    r = await cur.fetchone()
    credits = int(r["slip_credits"]) if r else 0
    if credits <= 0:
        return False
    await db.execute("UPDATE users SET slip_credits = slip_credits - 1 WHERE tg_user_id=?", (tg_user_id,))
    await db.commit()
    return True

# --- Drafts ---
async def get_or_create_draft(tg_user_id: int):
    db = await connect()
    cur = await db.execute("SELECT id, items_json FROM drafts WHERE tg_user_id=? ORDER BY id DESC LIMIT 1",
                           (tg_user_id,))
    row = await cur.fetchone()
    if row:
        items = json.loads(row["items_json"]) if row["items_json"] else []
        return {"id": row["id"], "items": items}
    await db.execute("INSERT INTO drafts (tg_user_id, items_json) VALUES (?, ?)", (tg_user_id, json.dumps([])))
    await db.commit()
    return await get_or_create_draft(tg_user_id)

async def save_draft(tg_user_id: int, items: List[Dict[str, Any]]) -> None:
    db = await connect()
    await db.execute("UPDATE drafts SET items_json=? WHERE tg_user_id=?", (json.dumps(items), tg_user_id))
    await db.commit()

async def clear_draft(tg_user_id: int) -> None:
    db = await connect()
    await db.execute("DELETE FROM drafts WHERE tg_user_id=?", (tg_user_id,))
    await db.commit()

# --- Slips ---
async def insert_slip(tg_user_id: int, items: List[Dict[str, Any]], combined_odds: float) -> int:
    db = await connect()
    now = int(time.time())
    expires = now + 10 * 24 * 3600
    cur = await db.execute(
        "INSERT INTO slips (tg_user_id, items_json, combined_odds, created_at, expires_at) VALUES (?, ?, ?, ?, ?)",
        (tg_user_id, json.dumps(items), combined_odds, now, expires))
    await db.commit()
    return cur.lastrowid  # type: ignore

async def list_slips(tg_user_id: int):
    db = await connect()
    cur = await db.execute("SELECT * FROM slips WHERE tg_user_id=? ORDER BY created_at DESC", (tg_user_id,))
    return await cur.fetchall()

async def cleanup_expired_slips() -> int:
    db = await connect()
    now = int(time.time())
    cur = await db.execute("DELETE FROM slips WHERE expires_at < ?", (now,))
    await db.commit()
    return cur.rowcount  # type: ignore

# --- Stripe sessions ---
async def add_stripe_session(tg_user_id: int, session_id: str, mode: str) -> None:
    db = await connect()
    await db.execute(
        "INSERT OR IGNORE INTO stripe_sessions (tg_user_id, session_id, mode, status) VALUES (?, ?, ?, 'open')",
        (tg_user_id, session_id, mode))
    await db.commit()

async def mark_session_status(session_id: str, status: str) -> None:
    db = await connect()
    await db.execute("UPDATE stripe_sessions SET status=? WHERE session_id=?", (status, session_id))
    await db.commit()

