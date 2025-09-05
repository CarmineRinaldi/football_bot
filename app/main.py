from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
import os

app = FastAPI()

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(bot)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.process_update(update)
    return {"ok": True}
