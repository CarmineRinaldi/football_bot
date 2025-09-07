import os
import requests
from db import add_user, get_user_plan, add_ticket, get_user_tickets
from football_api import get_leagues, get_national_teams, get_matches, search_teams, filter_by_letter
from datetime import datetime

FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# --------------------------
# Funzione invio messaggi
# --------------------------
def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{BASE_URL}/sendMessage", json=payload)

# --------------------------
# Menu principale e piani
# --------------------------
def start(update, context):
    user_id = update["message"]["from"]["id"]
    add_user(user_id)
    msg, markup = build_main_menu()
    send_message(user_id, msg, markup)
    return {"status": "ok"}

def build_main_menu():
    keyboard = [
        [{"text": "Free Plan 🆓", "callback_data": "plan_free"}],
        [{"text": "2€ Pack 💶", "callback_data": "plan_2eur"}],
        [{"text": "VIP Monthly 👑", "callback_data": "plan_vip"}],
        [{"text": "Le mie schedine 📋", "callback_data": "my_tickets"}]
    ]
    message = "⚽ Benvenuto nel tuo stadio personale!\nScegli un piano o controlla le tue schedine:"
    reply_markup = {"inline_keyboard": keyboard}
    return message, reply_markup

def show_plan_info(user_id, plan):
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
    send_message(user_id, text, {"inline_keyboard": keyboard})

# --------------------------
# Selezione tipo
# --------------------------
def show_search_choice(user_id, type_, plan):
    tipo_testo = "campionato" if type_ == "league" else "nazionale"
    keyboard = [
        [{"text": "Per lettera 🔤", "callback_data": f"search_letter_{type_}_{plan}"}],
        [{"text": "Per nome 🔎", "callback_data": f"search_name_{type_}_{plan}"}],
        [{"text": "🔙 Indietro", "callback_data": "back"}],
        [{"text": "🏟️ Menù principale calcistico", "callback_data": "main_menu"}]
    ]
    send_message(user_id, f"🔍 Scegli come cercare il {tipo_testo}:", {"inline_keyboard": keyboard})

# --------------------------
# Filtri alfabetici e ricerca
# --------------------------
def show_alphabet_keyboard(user_id, plan, type_):
    keyboard = [[{"text": c, "callback_data": f"filter_{type_}_{c}_{plan}"}] for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    tipo_testo = "campionato" if type_ == "league" else "nazionale"
    send_message(user_id, f"🔤 Filtra per lettera iniziale del {tipo_testo}:", {"inline_keyboard": keyboard})

def show_filtered_options(user_id, type_, letter, plan):
    items = get_leagues() if type_ == "league" else get_national_teams()
    filtered = filter_by_letter(items, "display_name", letter)

    if not filtered:
        send_message(user_id, f"😕 Nessun {type_} trovato con la lettera '{letter}'.")
        return

    keyboard = [[{"text": o["display_name"], "callback_data": f"{type_}_{o['league']['id']}_{plan}"}] for o in filtered]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    send_message(user_id, f"🏟️ Seleziona {type_}:", {"inline_keyboard": keyboard})

# --------------------------
# Mostra partite
# --------------------------
def show_matches(user_id, league_id, plan):
    matches = get_matches(league_id)
    if not matches:
        send_message(user_id, "⚽ Nessuna partita disponibile per questa competizione!")
        return

    keyboard = [[{"text": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}",
                  "callback_data": f"match_{m['fixture']['id']}_{plan}"}] for m in matches]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    send_message(user_id, "⚽ Seleziona fino a 5 partite per il pronostico giornaliero:", {"inline_keyboard": keyboard})

# --------------------------
# Ricerca squadra
# --------------------------
def search_team_prompt(user_id, plan):
    send_message(user_id, "🔎 Scrivi il nome della squadra che vuoi cercare:")

def show_search_results(user_id, query, plan, type_=None):
    results = search_teams(query, type_)
    if not results:
        send_message(user_id, f"😕 Nessun risultato trovato per '{query}'.")
        return

    keyboard = [[{"text": r["team"], "callback_data": f"team_{r['match_id']}_{plan}"}] for r in results]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    send_message(user_id, f"🔍 Risultati per '{query}':", {"inline_keyboard": keyboard})

# --------------------------
# Gestione tasti generici
# --------------------------
def handle_back(user_id, last_state, context={}):
    if last_state == "plan_info":
        show_plan_info(user_id, context.get("current_plan"))
    else:
        msg, markup = build_main_menu()
        send_message(user_id, msg, markup)
