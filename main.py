import os
from fastapi import FastAPI, Request
from db import init_db, delete_old_tickets
from bot_logic import start, show_main_menu, show_leagues, show_matches, create_ticket
from stripe_webhook import handle_stripe_event

init_db()  # crea le tabelle al deploy
delete_old_tickets()  # pulizia schedine vecchie

app = FastAPI()

@app.get("/")
async def root():
    return "Bot online!"

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    print("Webhook ricevuto:", data)

    if "message" in data and "text" in data["message"]:
        text = data["message"]["text"]
        if text == "/start":
            return start(data, None)

    if "callback_query" in data:
        cb = data["callback_query"]
        if cb["data"].startswith("plan_"):
            return show_main_menu(data, None)
        if cb["data"].startswith("league_"):
            league_id = int(cb["data"].split("_")[1])
            return show_matches(data, None, league_id)

    return {"status": 200}

@app.post("/stripe_webhook")
async def stripe_webhook(req: Request):
    payload = await req.body()
    sig_header = req.headers.get("stripe-signature")
    return handle_stripe_event(payload, sig_header)
