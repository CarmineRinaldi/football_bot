# webhook_server.py
from fastapi import FastAPI
from queue_handler import UpdateQueue

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from app.config import TG_BOT_TOKEN, WEBHOOK_PATH
from app.bot.handlers import start_handler

app = FastAPI()
bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(bot)

update_queue = UpdateQueue()
queue_task = None  # terrà il riferimento al task

@app.on_event("startup")
async def startup_event():
    global queue_task
    queue_task = asyncio.create_task(update_queue.process_queue())

@app.on_event("shutdown")
async def shutdown_event():
    await update_queue.stop()
    if queue_task:
        queue_task.cancel()
        try:
            await queue_task
        except asyncio.CancelledError:
            pass

@app.post(WEBHOOK_PATH)
async def telegram_webhook(update: dict):
    await update_queue.add_to_queue(Update(**update))
    return {"status": "ok"}

# registra handler
dp.register_message_handler(start_handler, commands=["start"])
