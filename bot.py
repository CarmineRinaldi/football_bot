import os, logging, asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import web
from handlers import start, free, vip, search
from db import init_db

logging.basicConfig(level=logging.INFO)

# Token e URL presi da environment
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = "/"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# Init DB
init_db()

# Registrazione handler
start.register_handlers(dp)
free.register_handlers(dp)
vip.register_handlers(dp)
search.register_handlers(dp)

# Startup/shutdown webhook
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    logging.info(f"Webhook impostato su {WEBHOOK_URL}")

async def on_shutdown():
    logging.info("🛑 Bot shutdown completato.")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()

if __name__ == "__main__":
    app = web.Application()
    web.setup_application(app, dp, on_startup=on_startup, on_shutdown=on_shutdown)
    web.run_app(app, host="0.0.0.0", port=10000)
