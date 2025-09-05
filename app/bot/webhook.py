# webhook_server.py
from fastapi import FastAPI, APIRouter, Request, Response
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from app.config import TG_BOT_TOKEN, WEBHOOK_PATH
from app.bot.handlers import start_handler
from app.queue_handler import update_queue  # istanza globale già creata

bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(bot)

router = APIRouter()

@router.post(WEBHOOK_PATH)
async def telegram_webhook(update: dict):
    """
    Riceve l'update da Telegram e lo mette nella coda
    invece di processarlo subito.
    """
    # Aggiunge l'update alla coda
    await update_queue.add_to_queue(Update(**update))
    return Response(status_code=200)

# Registra handler
dp.register_message_handler(start_handler, commands=["start"])

# Crea l'app FastAPI
app = FastAPI()
app.include_router(router)

# Avvia il processing della coda all'avvio dell'app
@app.on_event("startup")
async def startup_event():
    await update_queue.start()
    print("UpdateQueue avviata")

# Ferma il processing della coda alla chiusura dell'app
@app.on_event("shutdown")
async def shutdown_event():
    await update_queue.stop()
    print("UpdateQueue fermata")
