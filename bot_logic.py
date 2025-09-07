import os
import requests
from db import add_user, get_user_plan
from football_api import get_leagues, get_national_teams, get_matches, search_teams, filter_by_letter

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))


# --------------------------
# Funzione generica invio messaggi
# --------------------------
def send_message(chat_id, text, keyboard=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if keyboard:
        payload["reply_markup"] = {"inline_keyboard": keyboard}
    try:
        res = requests.post(BASE_URL, json=payload, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print("Errore invio messaggio:", e)


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
    send_message(chat_id, message, keyboard)


def show_plan_info(chat_id, plan):
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
    send_message(chat_id, text, keyboard)


# --------------------------
# Scelta tipo ricerca
# --------------------------
def show_search_choice(chat_id, type_, plan):
    tipo_testo = "campionato" if type_ == "league" else "nazionale"
    keyboard = [
        [{"text": "Per lettera 🔤", "callback_data": f"search_letter_{type_}_{plan}"}],
        [{"text": "Per nome 🔎", "callback_data": f"search_name_{type_}_{plan}"}],
        [{"text": "🔙 Indietro", "callback_data": "back"}],
        [{"text": "🏟️ Menù principale calcistico", "callback_data": "main_menu"}]
    ]
    send_message(chat_id, f"🔍 Scegli come cercare il {tipo_testo}:", keyboard)


# --------------------------
# Filtri alfabetici
# --------------------------
def show_alphabet_keyboard(chat_id, plan, type_):
    keyboard = [[{"text": c, "callback_data": f"filter_{type_}_{c}_{plan}"}] for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    tipo_testo = "campionato" if type_ == "league" else "nazionale"
    send_message(chat_id, f"🔤 Filtra per lettera iniziale del {tipo_testo}:", keyboard)


def show_filtered_options(chat_id, type_, letter, plan):
    items = get_leagues() if type_ == "league" else get_national_teams()
    filtered = filter_by_letter(items, "display_name", letter)

    if not filtered:
        send_message(chat_id, f"😕 Nessun {type_} trovato con la lettera '{letter}'.",
                     [[{"text": "🔙 Indietro", "callback_data": "back"}]])
        return

    keyboard = [[{"text": o["display_name"], "callback_data": f"{type_}_{o['league']['id']}_{plan}"}] for o in filtered]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    send_message(chat_id, f"🏟️ Seleziona {type_}:", keyboard)


# --------------------------
# Mostra partite
# --------------------------
def show_matches(chat_id, league_id, plan):
    matches = get_matches(league_id)
    if not matches:
        send_message(chat_id, "⚽ Nessuna partita disponibile per questa competizione!",
                     [[{"text": "🔙 Indietro", "callback_data": "back"}]])
        return

    keyboard = [[{"text": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}",
                  "callback_data": f"match_{m['fixture']['id']}_{plan}"}] for m in matches]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    send_message(chat_id, "⚽ Seleziona fino a 5 partite per il pronostico giornaliero:", keyboard)


# --------------------------
# Ricerca squadra
# --------------------------
def search_team_prompt(chat_id, plan):
    send_message(chat_id, "🔎 Scrivi il nome della squadra che vuoi cercare:")


def show_search_results(chat_id, query, plan, type_=None):
    results = search_teams(query, type_)
    if not results:
        send_message(chat_id, f"😕 Nessun risultato trovato per '{query}'.",
                     [[{"text": "🔙 Indietro", "callback_data": "back"}]])
        return

    keyboard = [[{"text": r["team"], "callback_data": f"team_{r['match_id']}_{plan}"}] for r in results]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    send_message(chat_id, f"🔍 Risultati per '{query}':", keyboard)
