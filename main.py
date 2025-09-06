import os
import json
import httpx
from fastapi import FastAPI, Request

# -----------------------------
# CONFIGURAZIONE TELEGRAM BOT
# -----------------------------
TOKEN = os.getenv("TELEGRAM_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

app = FastAPI()

# -----------------------------
# FUNZIONE DI INVIO MESSAGGI
# -----------------------------
async def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/sendMessage", json=payload)

# -----------------------------
# MENU PRINCIPALE
# -----------------------------
MAIN_MENU = {
    "inline_keyboard": [
        [{"text": "Free Plan 🆓", "callback_data": "plan_free"}],
        [{"text": "2€ Pack 💶", "callback_data": "plan_2eur"}],
        [{"text": "VIP Monthly 👑", "callback_data": "plan_vip"}],
        [{"text": "Le mie schedine 📋", "callback_data": "my_tickets"}],
    ]
}

# -----------------------------
# ENDPOINT HEALTHCHECK
# -----------------------------
@app.get("/")
async def root():
    return {"status": "ok"}

# -----------------------------
# WEBHOOK TELEGRAM
# -----------------------------
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    
    # Messaggi testuali
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        if text == "/start":
            await send_message(chat_id, "🎉 Benvenuto nel tuo bot calcistico super divertente! ⚽\nScegli un piano e iniziamo a creare le tue schedine!", MAIN_MENU)
            return {"ok": True}
    
    # Callback query
    elif "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["from"]["id"]
        data_cb = callback["data"]

        if data_cb == "plan_free":
            reply_markup = {
                "inline_keyboard": [
                    [{"text": "Scegli Campionato ⚽", "callback_data": "select_league_free"}],
                    [{"text": "🔙 Indietro", "callback_data": "main_menu"}]
                ]
            }
            await send_message(chat_id, "🆓 **Free Plan:** puoi creare fino a 5 partite per schedina. Scegli il tuo campionato preferito e divertiti!", reply_markup)
        
        elif data_cb == "select_league_free":
            reply_markup = {
                "inline_keyboard": [
                    [{"text": "🔙 Indietro", "callback_data": "plan_free"}]
                ]
            }
            await send_message(chat_id, "Seleziona il campionato che vuoi per la tua schedina:", reply_markup)
        
        elif data_cb == "main_menu":
            await send_message(chat_id, "Torna al menu principale:", MAIN_MENU)
        
        # TODO: aggiungere gestione altri piani, schedine e Stripe
        # elif data_cb == "plan_2eur":
        # elif data_cb == "plan_vip":
        # elif data_cb == "my_tickets":

        return {"ok": True}

    return {"ok": True}
