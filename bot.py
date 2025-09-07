import os
import logging
import asyncio
from aiogram import types, F
from aiogram.client.bot import Bot, DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.utils.keyboard import CallbackData

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- VARIABILI DALL'ENVIRONMENT ---
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Devi impostare la variabile TG_BOT_TOKEN!")

ADMIN_HTTP_TOKEN = os.getenv("ADMIN_HTTP_TOKEN")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "users.db")
FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET")
STRIPE_PRICE_2EUR = os.getenv("STRIPE_PRICE_2EUR")
STRIPE_PRICE_VIP = os.getenv("STRIPE_PRICE_VIP")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# --- CALLBACK DATA E BOT ---
example_cb = CallbackData("example", "action", "id")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# --- HANDLER DI ESEMPIO ---
async def start_handler(message: types.Message):
    await message.answer("⚽ FootballBot è online! Pronti a fare pronostici vincenti!")

# --- REGISTRA HANDLER ---
from aiogram import Dispatcher
dp = Dispatcher()
dp.message.register(start_handler, Command("start"))

# --- RUN BOT ---
async def main():
    # Se vuoi usare webhook su Render, qui puoi aggiungere la registrazione:
    # await bot.set_webhook(WEBHOOK_URL)
    
    logger.info("Bot avviato...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot fermato manualmente.")
