import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, Text
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers import start, free, vip, search

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Registriamo i callback e i comandi
start.register_handlers(dp)
free.register_handlers(dp)
vip.register_handlers(dp)
search.register_handlers(dp)

async def on_startup():
    logging.info(f"Bot avviato. Webhook impostato su {WEBHOOK_URL}")
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown():
    logging.info("🛑 Bot shutdown completato")
    await bot.delete_webhook()

if __name__ == "__main__":
    import asyncio
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
    from aiohttp import web

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/")

    logging.info("=== Avvio Bot ===")
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
