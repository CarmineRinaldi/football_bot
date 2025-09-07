import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode  # <-- import corretto per v3
from handlers import start, plans, search
from utils.db import init_db

# Inizializzazione database
init_db()

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)  # <-- usa ParseMode da aiogram.enums
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Registrazione handlers
start.register_handlers(dp)
plans.register_handlers(dp)
search.register_handlers(dp)

async def main():
    print("⚽ FootballBot è online! Pronti a fare pronostici vincenti!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
