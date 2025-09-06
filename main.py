import os
import httpx
from fastapi import FastAPI, Request
from db import init_db, delete_old_tickets
from bot_logic import start, show_main_menu, show_plan_info, show_leagues, show_matches, show_match_options, save_prediction
from stripe_webhook import handle_stripe_event

# Inizializza DB e pulizia schedine vecchie
init_db()
delete_old_tickets()

# Crea FastAPI app
app = FastAPI()

# Token Telegram
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"

async def send_message(chat_id, text, reply_markup=None):
    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": text,
            "reply_markup": reply_markup
        })

async def delete_message(chat_id, message_id):
    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/deleteMessage", json={
            "chat_id": chat_id,
            "message_id": message_id
        })

@app.get("/")
async def root():
    return {"status": "Bot online!"}

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    print("Webhook ricevuto:", data)

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        message_id = data["message"]["message_id"]
        text = data["message"]["text"]

        if text == "/start":
            await delete_message(chat_id, message_id)
            response = start(data, None)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

    if "callback_query" in data:
        cb = data["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        message_id = cb["message"]["message_id"]
        cb_data = cb["data"]

        await delete_message(chat_id, message_id)

        if cb_data == "main_menu":
            response = show_main_menu(data, None)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

        elif cb_data in ["plan_free", "plan_2eur", "plan_vip"]:
            plan = cb_data.split("_")[1]
            response = show_plan_info(data, None, plan)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

        elif cb_data.startswith("select_league_"):
            plan = cb_data.split("_")[-1]
            response = show_leagues(data, None, plan)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

        elif cb_data.startswith("league_"):
            parts = cb_data.split("_")
            league_id = int(parts[1])
            plan = parts[2]
            response = show_matches(data, None, league_id, plan)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

        elif cb_data.startswith("match_"):
            parts = cb_data.split("_")
            match_id = int(parts[1])
            plan = parts[2]
            response = show_match_options(data, None, match_id, plan)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

        elif cb_data.startswith("predict_"):
            parts = cb_data.split("_")
            match_id = int(parts[1])
            prediction = parts[2]
            plan = parts[3]
            user_id = cb["from"]["id"]
            response = save_prediction(user_id, match_id, prediction)
            await send_message(chat_id, response["text"])

@app.post("/stripe_webhook")
async def stripe_webhook(req: Request):
    payload = await req.body()
    sig_header = req.headers.get("stripe-signature")
    return handle_stripe_event(payload, sig_header)
