import os
import requests
import json
from datetime import datetime, timedelta
from db import get_user, create_user, save_ticket, get_tickets, delete_old_tickets

TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
FREE_MAX_MATCHES = int(os.environ["FREE_MAX_MATCHES"])
VIP_MAX_MATCHES = int(os.environ["VIP_MAX_MATCHES"])
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

BASE_URL = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"

def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    r = requests.post(f"{BASE_URL}/sendMessage", data=payload)
    return r.json()

def delete_message(chat_id, message_id):
    requests.post(f"{BASE_URL}/deleteMessage", data={"chat_id": chat_id, "message_id": message_id})

def handle_update(update):
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        # controllo /start
        if text.startswith("/start"):
            user = get_user(chat_id)
            if not user:
                create_user(chat_id)
            show_main_menu(chat_id)
            return

def show_main_menu(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "Free Plan", "callback_data": "plan_free"}],
            [{"text": "2€ Pack", "callback_data": "plan_2eur"}],
            [{"text": "VIP Monthly", "callback_data": "plan_vip"}],
            [{"text": "Le mie schedine", "callback_data": "my_tickets"}]
        ]
    }
    send_message(chat_id, "Benvenuto! Scegli un piano o controlla le tue schedine:", keyboard)

# altri handler per callback query (piani, creazione schedine, scelta squadre, quote)
# TODO: aggiungere logica scelta squadre + quote reali
