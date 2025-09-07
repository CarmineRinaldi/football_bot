import os
import httpx
from fastapi import FastAPI, Request
from db import init_db, delete_old_tickets
from bot_logic import (
    start, show_main_menu, show_plan_info,
    show_alphabet_keyboard, show_filtered_options,
    show_matches, search_team_prompt, show_search_results
)
from stripe_webhook import handle_stripe_event

# --------------------------
# Setup
# --------------------------

init_db()
delete_old_tickets()

app = FastAPI()
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"

# Per memorizzare utenti in modalità "ricerca squadra"
user_search_mode = {}

# --------------------------
# Funzioni Telegram
# --------------------------

async def send_message(chat_id, text, reply_markup=None):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": text,
            "reply_markup": reply_markup,
            "parse_mode": "Markdown"
        })
        return res.json().get("result", {}).get("message_id")

async def delete_message(chat_id, message_id):
    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/deleteMessage", json={
            "chat_id": chat_id,
            "message_id": message_id
        })

async def send_waiting_message(chat_id):
    return await send_message(chat_id, "⏳ Attendere prego...")

# --------------------------
# Webhook
# --------------------------

@app.get("/")
async def root():
    return {"status": "Bot online!"}

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    print("Webhook ricevuto:", data)

    chat_id = None
    plan = "free"

    # --------------------------
    # Messaggi testuali
    # --------------------------
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        message_id = data["message"]["message_id"]
        text = data["message"].get("text")

        if user_search_mode.get(chat_id):
            query = text.strip()
            await delete_message(chat_id, message_id)
            response = show_search_results(query, user_search_mode[chat_id], chat_id)
            await send_message(chat_id, response["text"], response.get("reply_markup"))
            user_search_mode.pop(chat_id)
            return {"status": 200}

        if text == "/start":
            await delete_message(chat_id, message_id)
            response = start(data, None)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

    # --------------------------
    # Callback Query
    # --------------------------
    if "callback_query" in data:
        cb = data["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        message_id = cb["message"]["message_id"]
        cb_data = cb["data"]

        await delete_message(chat_id, message_id)
        waiting_msg_id = await send_waiting_message(chat_id)

        # Menu principale
        if cb_data == "main_menu":
            response = show_main_menu(data, None)
            await send_message(chat_id, response["text"], response.get("reply_markup"))
        elif cb_data in ["plan_free", "plan_2eur", "plan_vip"]:
            plan = cb_data.split("_")[1]
            response = show_plan_info(data, None, plan, chat_id)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

        # Ricerca squadra
        elif cb_data.startswith("search_team_"):
            plan = cb_data.split("_")[2]
            user_search_mode[chat_id] = plan
            response = search_team_prompt(plan, chat_id)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

        # Altri livelli (campionati, nazionali, alfabetici, risultati) si gestiscono qui in modo analogo

    return {"status": 200}
