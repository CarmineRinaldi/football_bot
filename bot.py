import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.callback_data import CallbackData
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types.web_app_info import WebAppInfo

# Configurazione logging
logging.basicConfig(level=logging.INFO)

# Variabili d'ambiente
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN:
    raise ValueError("Devi impostare la variabile TG_BOT_TOKEN!")

# Bot e dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Esempio semplice di comando /start
@dp.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    await message.answer(
        f"Ciao <b>{message.from_user.full_name}</b>! Benvenuto nel bot di Football!",
    )

# Esempio di echo
@dp.message()
async def echo_message(message: Message):
    await message.answer(f"Hai scritto: {message.text}")

# Avvio webhook per Render
async def main():
    # Set webhook
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook impostato su {WEBHOOK_URL}")
    
    # Start polling come fallback (Render lo usa solo se vuoi)
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
