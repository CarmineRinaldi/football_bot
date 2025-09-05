from __future__ import annotations
import asyncio
from . import database

async def start_cleanup_loop() -> None:
    while True:
        try:
            await database.cleanup_expired_slips()
        except Exception:
            pass
        await asyncio.sleep(3600)  # ogni ora
