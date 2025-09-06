import os
import httpx
from fastapi import FastAPI, Request
from db import init_db, delete_old_tickets
from bot_logic import (
    start, show_main_menu, show_plan_info, 
    show_leagues, show_national_teams, show_matches, make_prediction
)

# Inizializza DB e pulizia schedine vecchie
init_db()
delete_old_tickets()

# FastAPI app
app = FastAPI()

# Telegram bot token
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

        elif cb_data == "plan_free":
            response = show_plan_info(data, None, "free")
            await send_message(chat_id, response["text"], response.get("reply_markup"))

        elif cb_data == "choose_league":
            response = show_leagues(data, None)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

        elif cb_data == "choose_national":
            response = show_national_teams(data, None)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

        elif cb_data.startswith("league_"):
            league_id = int(cb_data.split("_")[1])
            response = show_matches(data, None, league_id)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

        elif cb_data.startswith("team_"):
            match_id = int(cb_data.split("_")[1])
            response = make_prediction(data, None, match_id)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

    return {"status": 200}
