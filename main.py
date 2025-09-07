import os
import httpx
from fastapi import FastAPI, Request
from db import init_db, delete_old_tickets
from bot_logic import (
    start,
    show_main_menu,
    show_plan_info,
    show_leagues,
    show_nationals,
    show_matches,
    create_ticket,
)
from stripe_webhook import handle_stripe_event

# Inizializza DB e pulizia schedine vecchie
init_db()
delete_old_tickets()

app = FastAPI()

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"

async def send_message(chat_id, text, reply_markup=None):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            await client.post(f"{BASE_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": text,
                "reply_markup": reply_markup
            })
        except httpx.RequestError as e:
            print("Errore invio messaggio:", e)

async def delete_message(chat_id, message_id):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            await client.post(f"{BASE_URL}/deleteMessage", json={
                "chat_id": chat_id,
                "message_id": message_id
            })
        except httpx.RequestError as e:
            print("Errore cancellazione messaggio:", e)

@app.get("/")
async def root():
    return {"status": "Bot online!"}

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    print("Webhook ricevuto:", data)

    chat_id = None

    try:
        if "message" in data:
            msg = data["message"]
            chat_id = msg["chat"]["id"]
            message_id = msg["message_id"]
            text = msg.get("text")

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
            elif cb_data in ["plan_free", "plan_2eur", "plan_vip"]:
                plan = cb_data.split("_")[1]
                response = show_plan_info(data, None, plan)
            elif cb_data.startswith("select_league_"):
                plan = cb_data.split("_")[-1]
                response = show_leagues(data, None, plan)
            elif cb_data.startswith("select_national_"):
                plan = cb_data.split("_")[-1]
                response = show_nationals(data, None, plan)
            elif cb_data.startswith("league_") or cb_data.startswith("national_"):
                parts = cb_data.split("_")
                # Controllo se è un ID numerico o un comando (page)
                if parts[1].isdigit():
                    league_id = int(parts[1])
                    plan = parts[2] if len(parts) > 2 else "free"
                    response = show_matches(data, None, league_id, plan)
                else:
                    # Qui gestiamo comandi come "page_1" ecc.
                    print("Callback non numerico:", cb_data)
                    return {"status": 200}

            else:
                print("Callback non gestito:", cb_data)
                return {"status": 200}

            await send_message(chat_id, response["text"], response.get("reply_markup"))

    except Exception as e:
        print("Errore nel webhook:", e)

    return {"status": 200}

@app.post("/stripe_webhook")
async def stripe_webhook(req: Request):
    payload = await req.body()
    sig_header = req.headers.get("stripe-signature")
    return handle_stripe_event(payload, sig_header)
