import os
import requests
from db import add_user, get_user_plan
from football_api import get_leagues, get_national_teams, get_matches, search_teams, filter_by_letter

# --------------------------
# Config
# --------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))

# --------------------------
# Helper Telegram
# --------------------------
def send_message(chat_id, text, keyboard=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if keyboard:
        data["reply_markup"] = {"inline_keyboard": keyboard}
    requests.post(f"{BASE_URL}/sendMessage", json=data)

# --------------------------
# Start & Menù principale
# --------------------------
def start(update, context):
    user_id = update["message"]["from"]["id"]
    add_user(user_id)
    show_main_menu(update, context, send=True)

def show_main_menu(update, context, send=False):
    keyboard = [
        [{"text": "Free Plan 🆓", "callback_data": "plan_free"}],
        [{"text": "2€ Pack 💶", "callback_data": "plan_2eur"}],
        [{"text": "VIP Monthly 👑", "callback_data": "plan_vip"}],
        [{"text": "Le mie schedine 📋", "callback_data": "my_tickets"}]
    ]
    message = "⚽ Benvenuto nel tuo stadio personale!\nScegli un piano o controlla le tue schedine:"
    if send:
        chat_id = update["message"]["from"]["id"]
        send_message(chat_id, message, keyboard)
    else:
        return {"text": message, "reply_markup": {"inline_keyboard": keyboard}}

# --------------------------
# Info piano
# --------------------------
def show_plan_info(update, context, plan, send=False):
    chat_id = update["message"]["from"]["id"] if "message" in update else update["callback_query"]["from"]["id"]

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
    if send:
        send_message(chat_id, text, keyboard)
    else:
        return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}

# --------------------------
# Selezione tipo: lettera o nome
# --------------------------
def show_search_choice(update, context, type_, plan, send=False):
    chat_id = update["message"]["from"]["id"] if "message" in update else update["callback_query"]["from"]["id"]
    tipo_testo = "campionato" if type_ == "league" else "nazionale"
    keyboard = [
        [{"text": "Per lettera 🔤", "callback_data": f"search_letter_{type_}_{plan}"}],
        [{"text": "Per nome 🔎", "callback_data": f"search_name_{type_}_{plan}"}],
        [{"text": "🔙 Indietro", "callback_data": "back"}],
        [{"text": "🏟️ Menù principale calcistico", "callback_data": "main_menu"}]
    ]
    text = f"🔍 Scegli come cercare il {tipo_testo}:"
    if send:
        send_message(chat_id, text, keyboard)
    else:
        return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}

# --------------------------
# Filtri alfabetici
# --------------------------
def show_alphabet_keyboard(update, context, plan, type_, send=False):
    chat_id = update["message"]["from"]["id"] if "message" in update else update["callback_query"]["from"]["id"]
    keyboard = [[{"text": c, "callback_data": f"filter_{type_}_{c}_{plan}"}] for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    tipo_testo = "campionato" if type_ == "league" else "nazionale"
    text = f"🔤 Filtra per lettera iniziale del {tipo_testo}:"
    if send:
        send_message(chat_id, text, keyboard)
    else:
        return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}

def show_filtered_options(update, context, type_, letter, plan, send=False):
    chat_id = update["message"]["from"]["id"] if "message" in update else update["callback_query"]["from"]["id"]
    items = get_leagues() if type_ == "league" else get_national_teams()
    filtered = filter_by_letter(items, "display_name", letter)
    if not filtered:
        text = f"😕 Nessun {type_} trovato con la lettera '{letter}'."
        keyboard = [[{"text": "🔙 Indietro", "callback_data": "back"}]]
        if send:
            send_message(chat_id, text, keyboard)
        else:
            return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}
        return

    keyboard = [[{"text": o["display_name"], "callback_data": f"{type_}_{o['league']['id']}_{plan}"}] for o in filtered]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    text = f"🏟️ Seleziona {type_}:"
    if send:
        send_message(chat_id, text, keyboard)
    else:
        return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}

# --------------------------
# Mostra partite
# --------------------------
def show_matches(update, context, league_id, plan, send=False):
    chat_id = update["message"]["from"]["id"] if "message" in update else update["callback_query"]["from"]["id"]
    matches = get_matches(league_id)
    if not matches:
        text = "⚽ Nessuna partita disponibile per questa competizione!"
        keyboard = [[{"text": "🔙 Indietro", "callback_data": "back"}]]
        if send:
            send_message(chat_id, text, keyboard)
        else:
            return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}
        return

    keyboard = [[{"text": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}",
                  "callback_data": f"match_{m['fixture']['id']}_{plan}"}] for m in matches]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    text = "⚽ Seleziona fino a 5 partite per il pronostico giornaliero:"
    if send:
        send_message(chat_id, text, keyboard)
    else:
        return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}

# --------------------------
# Ricerca squadra
# --------------------------
def search_team_prompt(update, context, plan, send=False):
    chat_id = update["message"]["from"]["id"] if "message" in update else update["callback_query"]["from"]["id"]
    text = "🔎 Scrivi il nome della squadra che vuoi cercare:"
    if send:
        send_message(chat_id, text)
    else:
        return {"text": text, "reply_markup": None}

def show_search_results(update, context, query, plan, type_=None, send=False):
    chat_id = update["message"]["from"]["id"] if "message" in update else update["callback_query"]["from"]["id"]
    results = search_teams(query, type_)
    if not results:
        text = f"😕 Nessun risultato trovato per '{query}'."
        keyboard = [[{"text": "🔙 Indietro", "callback_data": "back"}]]
        if send:
            send_message(chat_id, text, keyboard)
        else:
            return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}
        return

    keyboard = [[{"text": r["team"], "callback_data": f"team_{r['match_id']}_{plan}"}] for r in results]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    text = f"🔍 Risultati per '{query}':"
    if send:
        send_message(chat_id, text, keyboard)
    else:
        return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}
