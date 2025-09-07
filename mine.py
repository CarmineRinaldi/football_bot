from db import add_user, get_user_plan, add_ticket, get_user_tickets
from football_api import get_leagues, get_national_teams, get_matches, search_teams, filter_by_letter
from datetime import datetime
import os

FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))

# --------------------------
# Menu principale e piani
# --------------------------
def start(update, context):
    user_id = update["message"]["from"]["id"]
    add_user(user_id)
    return show_main_menu(update, context)

def show_main_menu(update, context):
    keyboard = [
        [{"text": "Free Plan 🆓", "callback_data": "plan_free"}],
        [{"text": "2€ Pack 💶", "callback_data": "plan_2eur"}],
        [{"text": "VIP Monthly 👑", "callback_data": "plan_vip"}],
        [{"text": "Le mie schedine 📋", "callback_data": "my_tickets"}]
    ]
    message = "⚽ Benvenuto nel tuo stadio personale!\nScegli un piano o controlla le tue schedine:"
    return {"text": message, "reply_markup": {"inline_keyboard": keyboard}}

def show_plan_info(update, context, plan):
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
    return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}

# --------------------------
# Selezione tipo
# --------------------------
def show_search_choice(type_, plan):
    tipo_testo = "campionato" if type_ == "league" else "nazionale"
    keyboard = [
        [{"text": "Per lettera 🔤", "callback_data": f"search_letter_{type_}_{plan}"}],
        [{"text": "Per nome 🔎", "callback_data": f"search_name_{type_}_{plan}"}],
        [{"text": "🔙 Indietro", "callback_data": "back"}],
        [{"text": "🏟️ Menù principale calcistico", "callback_data": "main_menu"}]
    ]
    return {"text": f"🔍 Scegli come cercare il {tipo_testo}:", "reply_markup": {"inline_keyboard": keyboard}}

# --------------------------
# Filtri alfabetici e ricerca
# --------------------------
def show_alphabet_keyboard(plan, type_):
    keyboard = [[{"text": c, "callback_data": f"filter_{type_}_{c}_{plan}"}] for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    tipo_testo = "campionato" if type_ == "league" else "nazionale"
    return {"text": f"🔤 Filtra per lettera iniziale del {tipo_testo}:", "reply_markup": {"inline_keyboard": keyboard}}

def show_filtered_options(type_, letter, plan):
    items = get_leagues() if type_ == "league" else get_national_teams()
    filtered = filter_by_letter(items, "display_name", letter)

    if not filtered:
        return {
            "text": f"😕 Nessun {type_} trovato con la lettera '{letter}'.",
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 Indietro", "callback_data": "back"}]]}
        }

    keyboard = [[{"text": o["display_name"], "callback_data": f"{type_}_{o['league']['id']}_{plan}"}] for o in filtered]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    return {"text": f"🏟️ Seleziona {type_}:", "reply_markup": {"inline_keyboard": keyboard}}

# --------------------------
# Mostra partite
# --------------------------
def show_matches(update, context, league_id, plan):
    matches = get_matches(league_id)
    if not matches:
        return {
            "text": "⚽ Nessuna partita disponibile per questa competizione!",
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 Indietro", "callback_data": "back"}]]}
        }

    keyboard = [[{"text": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}",
                  "callback_data": f"match_{m['fixture']['id']}_{plan}"}] for m in matches]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    return {
        "text": "⚽ Seleziona fino a 5 partite per il pronostico giornaliero:",
        "reply_markup": {"inline_keyboard": keyboard}
    }

# --------------------------
# Ricerca squadra
# --------------------------
def search_team_prompt(plan):
    return {"text": "🔎 Scrivi il nome della squadra che vuoi cercare:", "reply_markup": None}

def show_search_results(query, plan, type_=None):
    results = search_teams(query, type_)
    if not results:
        return {
            "text": f"😕 Nessun risultato trovato per '{query}'.",
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 Indietro", "callback_data": "back"}]]}
        }

    keyboard = [[{"text": r["team"], "callback_data": f"team_{r['match_id']}_{plan}"}] for r in results]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    return {"text": f"🔍 Risultati per '{query}':", "reply_markup": {"inline_keyboard": keyboard}}

# --------------------------
# Gestione tasti generici
# --------------------------
def handle_back(update, context, last_state):
    if last_state == "plan_info":
        return show_plan_info(update, context, context.get("current_plan"))
    else:
        return show_main_menu(update, context)
