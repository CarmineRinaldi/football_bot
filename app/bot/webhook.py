from fastapi import APIRouter, Request, Response
from aiogram import Bot, Dispatcher
from app.config import TG_BOT_TOKEN, WEBHOOK_PATH
from app.bot.handlers import start_handler
from aiogram.types import Update

bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(bot)

router = APIRouter()

@router.post(WEBHOOK_PATH)
async def telegram_webhook(update: dict):
    telegram_update = Update(**update)
    await dp.process_update(telegram_update)
    return Response(status_code=200)

dp.register_message_handler(start_handler, commands=["start"])
