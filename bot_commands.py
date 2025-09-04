import os
import aiohttp
from db_handler import DBHandler
from payments import StripeHandler

TELEGRAM_TOKEN = os.environ.get("TG_BOT_TOKEN")
DB = DBHandler()
STRIPE = StripeHandler()

async def handle_update(update):
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        if text.startswith("/start"):
            await send_message(chat_id, "Benvenuto! Usa /help per i comandi.")
        elif text.startswith("/help"):
            await send_message(chat_id, "/vip - Acquista VIP\n/status - Stato partite")
        elif text.startswith("/vip"):
            await handle_vip(chat_id)
        elif text.startswith("/status"):
            await send_message(chat_id, DB.get_status(chat_id))
        else:
            await send_message(chat_id, "Comando non riconosciuto. Usa /help.")

async def handle_vip(chat_id):
    payment_url = STRIPE.create_payment_url(chat_id)
    await send_message(chat_id, f"Acquista VIP qui: {payment_url}")

async def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    async with aiohttp.ClientSession() as session:
        await session.post(url, json={"chat_id": chat_id, "text": text})
