import os
import logging
from aiogram import Dispatcher
from aiogram.client.bot import Bot, DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- VARIABILI DALL'ENVIRONMENT ---
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Devi impostare la variabile TG_BOT_TOKEN!")

WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # es: https://tuo-bot.onrender.com/webhook
PORT = int(os.getenv("PORT", 8080))

# --- CREA BOT E DISPATCHER ---
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# --- REGISTRA HANDLER ---
from handlers import start_handler, plans_handler, search_handler

start_handler.register_handlers(dp)
plans_handler.register_handlers(dp)
search_handler.register_handlers(dp)

# --- FUNZIONI DI STARTUP E SHUTDOWN ---
async def on_startup(app: web.Application):
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook impostato su {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    await bot.session.close()

# --- CREAZIONE APP AIOHTTP ---
def main():
    app = web.Application()
    dp.setup(app)  # collega dispatcher ad aiohttp

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
