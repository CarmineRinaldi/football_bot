import os
import requests
from fastapi import FastAPI, Request
from db import init_db, delete_old_tickets
from bot_logic import start, show_main_menu, show_leagues, show_matches, create_ticket
from stripe_webhook import handle_stripe_event

# inizializza DB e pulizia schedine vecchie
init_db()
delete_old_tickets()

# FastAPI app
app = FastAPI()

# Telegram bot token
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"

@app.get("/")
async def root():
    return {"status": "Bot online!"}

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    print("Webhook ricevuto:", data)

    # Messaggi testuali
    if "message" in data and "text" in data["message"]:
        text = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        if text == "/start":
            response = start(data, None)
            requests.post(f"{BASE_URL}/sendMessage", json={"chat_id": chat_id, **response})

    # Callback query (inline buttons)
    if "callback_query" in data:
        cb = data["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        message_id = cb["message"]["message_id"]

        if cb["data"].startswith("plan_"):
            response = show_main_menu(data, None)
            requests.post(f"{BASE_URL}/editMessageText", json={
                "chat_id": chat_id,
                "message_id": message_id,
                **response
            })

        if cb["data"].startswith("league_"):
            league_id = int(cb["data"].split("_")[1])
            response = show_matches(data, None, league_id)
            requests.post(f"{BASE_URL}/editMessageText", json={
                "chat_id": chat_id,
                "message_id": message_id,
                **response
            })

    return {"status": 200}

@app.post("/stripe_webhook")
async def stripe_webhook(req: Request):
    payload = await req.body()
    sig_header = req.headers.get("stripe-signature")
    return handle_stripe_event(payload, sig_header)
