import os
import json
import logging
import httpx
from fastapi import FastAPI, Request
from db import init_db, delete_old_tickets
from bot_logic import start, show_main_menu, show_plan_info, show_leagues, show_matches
from stripe_webhook import handle_stripe_event

# -----------------------------
# Config logging
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------
# DB init
# -----------------------------
init_db()
delete_old_tickets()

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI()

# Telegram bot
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"

# -----------------------------
# Helper
# -----------------------------
def get_user_id(update):
    if "message" in update:
        return update["message"]["from"]["id"]
    elif "callback_query" in update:
        return update["callback_query"]["from"]["id"]
    return None

async def send_message(chat_id: int, text: str, reply_markup: dict = None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/sendMessage", json=payload)

async def edit_message(chat_id: int, message_id: int, text: str, reply_markup: dict = None):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/editMessageText", json=payload)

# -----------------------------
# Endpoints
# -----------------------------
@app.get("/")
async def root():
    return {"status": "Bot online!"}

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    logger.info(f"Webhook ricevuto: {data}")

    user_id = get_user_id(data)

    # Messaggi testuali
    if "message" in data and "text" in data["message"]:
        text = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        if text == "/start":
            response = start(data, None)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

    # Callback inline
    if "callback_query" in data:
        cb = data["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        message_id = cb["message"]["message_id"]
        cb_data = cb["data"]

        # Torna al menu principale
        if cb_data == "main_menu":
            response = show_main_menu(data, None)
            await edit_message(chat_id, message_id, response["text"], response.get("reply_markup"))

        # Piani
        elif cb_data in ["plan_free", "plan_2eur", "plan_vip"]:
            plan = cb_data.split("_")[1]
            response = show_plan_info(data, None, plan)
            await edit_message(chat_id, message_id, response["text"], response.get("reply_markup"))

        # Selezione campionato
        elif cb_data.startswith("select_league_"):
            plan = cb_data.split("_")[-1]
            response = show_leagues(data, None, plan)
            await edit_message(chat_id, message_id, response["text"], response.get("reply_markup"))

        # Scelta campionato
        elif cb_data.startswith("league_"):
            parts = cb_data.split("_")
            league_id = int(parts[1])
            plan = parts[2]
            response = show_matches(data, None, league_id, plan)
            await edit_message(chat_id, message_id, response["text"], response.get("reply_markup"))

    return {"status": 200}

@app.post("/stripe_webhook")
async def stripe_webhook(req: Request):
    payload = await req.body()
    sig_header = req.headers.get("stripe-signature")
    return handle_stripe_event(payload, sig_header)
