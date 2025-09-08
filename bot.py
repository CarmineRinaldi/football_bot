import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import start, plans, search

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = "/"  # può rimanere / per il routing principale

# Config bot con default parse_mode
from aiogram.client.bot import DefaultBotCommands, DefaultBotProperties
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))

dp = Dispatcher(storage=MemoryStorage())

# Registro gli handler
start.register_handlers(dp)
plans.register_handlers(dp)
search.register_handlers(dp)

async def on_startup():
    # Imposta il webhook
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    logging.info(f"Webhook impostato su {WEBHOOK_URL}")

async def on_shutdown():
    logging.info("🛑 Bot shutdown completato.")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()

if __name__ == "__main__":
    import asyncio
    from aiogram import web

    app = web.Application()
    web.setup_application(app, dp, on_startup=on_startup, on_shutdown=on_shutdown)

    # Lancia server aiohttp su porta 10000
    web.run_app(app, host="0.0.0.0", port=10000)
