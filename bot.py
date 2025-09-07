import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from handlers import start, plans, search, buttons
from utils.db import init_db

# Inizializzazione database
init_db()

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Registrazione handlers
start.register_handlers(dp)
plans.register_handlers(dp)
search.register_handlers(dp)

if __name__ == "__main__":
    from aiogram import executor
    print("⚽ FootballBot è online! Pronti a fare pronostici vincenti!")
    executor.start_polling(dp)
