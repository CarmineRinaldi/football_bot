from fastapi import FastAPI, Request
import asyncio
from bot.bot import bot, dp
from bot.queue_handler import UpdateQueue

app = FastAPI()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    # Metti l'update nella coda asincrona
    await UpdateQueue.queue.put(data)
    return {"ok": True}

# Background task per processare la coda
@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(UpdateQueue.process_queue(dp))
