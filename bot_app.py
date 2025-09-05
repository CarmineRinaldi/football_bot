# bot_app.py

import asyncio
from fastapi import FastAPI, Request, Response
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.filters import Command

# ---------------- CONFIG ----------------
TG_BOT_TOKEN = "IL_TUO_TOKEN_TELEGRAM"
WEBHOOK_PATH = "/webhook"

# ---------------- CODA ASINCRONA ----------------
class UpdateQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.running = False

    async def process_queue(self):
        """Processa gli aggiornamenti nella coda."""
        self.running = True
        while self.running:
            item = await self.queue.get()
            try:
                # Qui puoi gestire il tuo item (es. invio messaggi, logging, ecc.)
                print(f"Processing item: {item}")
            except Exception as e:
                print(f"Errore durante il processing: {e}")
            finally:
                self.queue.task_done()

    async def add_to_queue(self, item):
        """Aggiunge un item alla coda."""
        await self.queue.put(item)

    async def stop(self):
        """Ferma il processing della coda."""
        self.running = False
        await self.queue.join()

# ---------------- BOT & DISPATCHER ----------------
bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(bot)

# Coda globale
update_queue = UpdateQueue()
queue_task = None

# ---------------- FASTAPI APP ----------------
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    global queue_task
    queue_task = asyncio.create_task(update_queue.process_queue())
    print("Coda avviata!")

@app.on_event("shutdown")
async def shutdown_event():
    await update_queue.stop()
    if queue_task:
        queue_task.cancel()
        try:
            await queue_task
        except asyncio.CancelledError:
            pass
    print("Coda fermata!")

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    """Riceve gli update da Telegram e li mette nella coda."""
    update_dict = await request.json()
    await update_queue.add_to_queue(Update(**update_dict))
    return Response(status_code=200)

# ---------------- HANDLER DI ESEMPIO ----------------
@dp.message(Command(commands=["start"]))
async def start_handler(message):
    await message.answer("Ciao! Bot pronto e in esecuzione.")

# ---------------- RUN CON GUNICORN ----------------
# Su Render: gunicorn bot_app:app --workers 1 --threads 2 --bind 0.0.0.0:$PORT
