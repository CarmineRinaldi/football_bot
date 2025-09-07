import os
import logging
import asyncio
from aiogram import Dispatcher, types, F
from aiogram.client.bot import Bot, DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiohttp import web

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- VARIABILI DALL'ENVIRONMENT ---
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Devi impostare la variabile TG_BOT_TOKEN!")

WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # es: https://football-bot-ric2.onrender.com/webhook
PORT = int(os.getenv("PORT", 8080))     # Render usa la variabile PORT

# --- CREA BOT E DISPATCHER ---
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# --- HANDLER ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("⚽ FootballBot è online con webhook!")

# --- APP AIOHTTP ---
async def on_startup(app: web.Application):
    # Cancella vecchi webhook e imposta quello nuovo
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook impostato su {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    await bot.session.close()

def main():
    app = web.Application()
    dp.setup(app)  # collega dispatcher ad aiohttp

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
