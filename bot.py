import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from handlers import start, search, plans  # Assicurati di avere __init__.py in handlers
from aiogram.client.session.aiohttp import AiohttpSession

BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Devi impostare la variabile BOT_TOKEN!")

# Inizializza bot e dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML, session=AiohttpSession())
dp = Dispatcher()

# Registra gli handler
start.register_handlers(dp)
search.register_handlers(dp)
plans.register_handlers(dp)

async def main():
    # Rimuove eventuale webhook attivo
    await bot.delete_webhook(drop_pending_updates=True)
    print("⚽ FootballBot è online! Pronti a fare pronostici vincenti!")

    # Avvia il polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
