import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils import exceptions

from handlers import start, search, plans
from buttons import main_menu

# -----------------------------
# Configurazione logging
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------
# Variabili d'ambiente
# -----------------------------
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Devi impostare la variabile BOT_TOKEN!")

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # opzionale, per webhook

# -----------------------------
# Inizializzazione Bot e Dispatcher
# -----------------------------
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher()

# -----------------------------
# Registrazione handler
# -----------------------------
start.register_handlers(dp)
search.register_handlers(dp)
plans.register_handlers(dp)

# -----------------------------
# Funzione main
# -----------------------------
async def main():
    if WEBHOOK_URL:
        # Se vuoi usare webhook (Render supporta HTTPS)
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await bot.set_webhook(WEBHOOK_URL)
            logger.info(f"Webhook impostato su {WEBHOOK_URL}")
        except exceptions.TelegramAPIError as e:
            logger.error(f"Errore impostando webhook: {e}")
    else:
        # Usa long polling
        logger.info("Avvio bot in modalità polling…")
        try:
            await dp.start_polling(bot)
        except exceptions.TelegramAPIError as e:
            logger.error(f"Errore polling: {e}")

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
