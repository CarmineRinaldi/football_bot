import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
if not TG_BOT_TOKEN:
    raise RuntimeError("TG_BOT_TOKEN non impostato nelle environment variables")

bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher()

# esempio handler minimale — sostituisci/estendi con i tuoi router/handler
@dp.message()
async def echo_handler(message: Message):
    await message.answer("Benvenuto! Usa i comandi dal menu per continuare.")

async def start_bot():
    # Avvia il polling (nota: in produzione è preferibile usare webhook, qui è semplice e funziona)
    await dp.start_polling(bot)
