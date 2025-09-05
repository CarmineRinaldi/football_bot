# webhook_server.py
from fastapi import APIRouter, Request, Response
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from app.config import TG_BOT_TOKEN, WEBHOOK_PATH
from app.bot.handlers import start_handler
from queue_handler import UpdateQueue  # il file che abbiamo creato

bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(bot)

# Coda globale per processare gli update
update_queue = UpdateQueue()

# Avvia il task della coda
import asyncio
asyncio.create_task(update_queue.process_queue())

router = APIRouter()

@router.post(WEBHOOK_PATH)
async def telegram_webhook(update: dict):
    """
    Riceve l'update da Telegram e lo mette nella coda
    invece di processarlo subito.
    """
    await update_queue.add_to_queue(Update(**update))
    return Response(status_code=200)

# Registra handler
dp.register_message_handler(start_handler, commands=["start"])
