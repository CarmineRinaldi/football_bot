import os
import time
import requests
from db import add_user, get_user_plan
from football_api import get_leagues, get_national_teams, get_matches, search_teams, filter_by_letter

# --------------------------
# Configurazione BOT
# --------------------------
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Errore: TG_BOT_TOKEN non impostato nel file .env")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))

# --------------------------
# Funzione invio messaggi
# --------------------------
def send_message(chat_id, text, keyboard=None, retries=3):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if keyboard:
        payload["reply_markup"] = {"inline_keyboard": keyboard}

    for attempt in range(retries):
        try:
            res = requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=10)
            res.raise_for_status()
            return res.json().get("result", {}).get("message_id")
        except Exception as e:
            print(f"[Tentativo {attempt+1}/{retries}] Errore invio messaggio:", e)
            time.sleep(2)
    return None

def delete_message(chat_id, message_id):
    try:
        res = requests.post(f"{BASE_URL}/deleteMessage", json={
            "chat_id": chat_id,
            "message_id": message_id
        }, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print("Errore eliminazione messaggio:", e)

# --------------------------
# Start e menu principale
# --------------------------
def start(update, context):
    chat_id = update["message"]["chat"]["id"]
    user_id = update["message"]["from"]["id"]
    add_user(user_id)
    show_main_menu(chat_id)

def show_main_menu(chat_id):
    keyboard = [
        [{"text": "Free Plan 🆓", "callback_data": "plan_free"}],
        [{"text": "2€ Pack 💶", "callback_data": "plan_2eur"}],
        [{"text": "VIP Monthly 👑", "callback_data": "plan_vip"}],
        [{"text": "Le mie schedine 📋", "callback_data": "my_tickets"}]
    ]
    message = "⚽ Benvenuto nel tuo stadio personale!\nScegli un piano o controlla le tue schedine:"
    return send_message(chat_id, message, keyboard)

def show_plan_info(chat_id, plan, old_msg_id=None):
    if old_msg_id:
        delete_message(chat_id, old_msg_id)

    if plan == "free":
        text = f"🆓 **Free Plan:** puoi fare fino a {FREE_MAX_MATCHES} pronostici al giorno, massimo 5 partite per pronostico!"
    elif plan == "2eur":
        text = "💶 **2€ Pack:** più pronostici giornalieri e funzionalità extra!"
    else:
        text = f"👑 **VIP:** massimo {VIP_MAX_MATCHES} pronostici al giorno, aggiornamenti e supporto VIP!"

    keyboard = [
        [{"text": "Campionati ⚽", "callback_data": f"select_type_league_{plan}"}],
        [{"text": "Nazionali 🌍", "callback_data": f"select_type_national_{plan}"}],
        [{"text": "Cerca squadra 🔎", "callback_data": f"search_team_{plan}"}],
        [{"text": "🏟️ Menù principale calcistico", "callback_data": "main_menu"}]
    ]
    return send_message(chat_id, text, keyboard)

# --------------------------
# (Le altre funzioni tipo show_search_choice, show_alphabet_keyboard, ecc.)
# Aggiungi anche lì il parametro old_msg_id e chiama delete_message(chat_id, old_msg_id)
# --------------------------
