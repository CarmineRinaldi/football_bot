from db import add_user, get_user_tickets
from football_api import get_leagues, get_national_teams, get_matches, search_teams
from datetime import datetime
import os

FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))

# --------------------------
# Dizionari per menu a livelli
# --------------------------
# user_last_menu: memorizza l'ultimo menu visitato per ciascun utente
user_last_menu = {}

# user_search_mode: memorizza l'utente in modalità ricerca squadra
user_search_mode = {}

# --------------------------
# Menu principale
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

# --------------------------
# Piani
# --------------------------
def show_plan_info(update, context, plan):
    user_id = update["message"]["from"]["id"]
    user_last_menu[user_id] = f"plan_{plan}"  # traccia il livello corrente

    if plan == "free":
        text = f"🆓 Free Plan: puoi fare fino a {FREE_MAX_MATCHES} pronostici al giorno, massimo 5 partite per pronostico!"
    elif plan == "2eur":
        text = "💶 2€ Pack: più pronostici giornalieri e funzionalità extra!"
    else:
        text = f"👑 VIP: massimo {VIP_MAX_MATCHES} pronostici al giorno, aggiornamenti e supporto VIP!"

    keyboard = [
        [{"text": "Scegli campionato ⚽", "callback_data": f"select_league_{plan}"}],
        [{"text": "Nazionali 🌍", "callback_data": f"select_national_{plan}"}],
        [{"text": "Cerca squadra 🔎", "callback_data": f"search_team_{plan}"}],
        [{"text": "🏟️ Menù principale ⚽", "callback_data": "main_menu"}]
    ]
    return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}

# --------------------------
# Tastiere alfabetiche e filtraggio
# --------------------------
def show_alphabet_keyboard(plan, type_):
    user_id = plan  # qui plan è callback_data originale (usiamo solo come chiave)
    keyboard = [[{"text": c, "callback_data": f"filter_{type_}_{c}_{plan}"}] for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": plan}])
    keyboard.append([{"text": "🏟️ Menù principale ⚽", "callback_data": "main_menu"}])
    tipo_testo = "campionato" if type_ == "league" else "nazionale"
    return {"text": f"🔍 Filtra per lettera iniziale del {tipo_testo}:", "reply_markup": {"inline_keyboard": keyboard}}

def show_filtered_options(type_, letter, plan):
    options = get_leagues() if type_ == "league" else get_national_teams()
    filtered = [o for o in options if o["league"]["name"].upper().startswith(letter.upper())]

    if not filtered:
        return {"text": f"😕 Nessun {type_} trovato con la lettera '{letter}'.",
                "reply_markup": {"inline_keyboard": [[{"text": "🔙 Indietro", "callback_data": plan}],
                                                     [{"text": "🏟️ Menù principale ⚽", "callback_data": "main_menu"}]]}}

    keyboard = [[{"text": o["display_name"], "callback_data": f"{type_}_{o['league']['id']}_{plan}"}] for o in filtered]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"select_{type_}_{plan}"}])
    keyboard.append([{"text": "🏟️ Menù principale ⚽", "callback_data": "main_menu"}])
    tipo_testo = "campionato" if type_ == "league" else "nazionale"
    return {"text": f"🏟️ Seleziona un {tipo_testo}:", "reply_markup": {"inline_keyboard": keyboard}}

# --------------------------
# Funzioni partite
# --------------------------
def show_matches(update, context, league_id, plan):
    user_id = update["message"]["from"]["id"]
    user_last_menu[user_id] = f"{plan}"  # salva livello precedente

    matches = get_matches(league_id)
    if not matches:
        return {"text": "⚽ Nessuna partita disponibile per questa competizione!",
                "reply_markup": {"inline_keyboard": [[{"text": "🔙 Indietro", "callback_data": f"select_league_{plan}"}],
                                                     [{"text": "🏟️ Menù principale ⚽", "callback_data": "main_menu"}]]}}

    keyboard = [[{"text": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}", 
                  "callback_data": f"match_{m['fixture']['id']}"}] for m in matches]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"select_league_{plan}"}])
    keyboard.append([{"text": "🏟️ Menù principale ⚽", "callback_data": "main_menu"}])
    return {"text": "⚽ Seleziona fino a 5 partite per il pronostico giornaliero:", 
            "reply_markup": {"inline_keyboard": keyboard}}

# --------------------------
# Ricerca squadra
# --------------------------
def search_team_prompt(plan):
    return {"text": "🔎 Scrivi il nome della squadra che vuoi cercare:", "reply_markup": None}

def show_search_results(query, plan):
    results = search_teams(query)
    if not results:
        return {"text": f"😕 Nessun risultato trovato per '{query}'.",
                "reply_markup": {"inline_keyboard": [[{"text": "🔙 Indietro", "callback_data": f"plan_{plan}"}],
                                                     [{"text": "🏟️ Menù principale ⚽", "callback_data": "main_menu"}]]}}

    keyboard = [[{"text": r["team"], "callback_data": f"team_{r['match_id']}_{plan}"}] for r in results]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"plan_{plan}"}])
    keyboard.append([{"text": "🏟️ Menù principale ⚽", "callback_data": "main_menu"}])
    return {"text": f"🔍 Risultati per '{query}':", "reply_markup": {"inline_keyboard": keyboard}}

# --------------------------
# Funzioni pronostici
# --------------------------
def can_create_pronostic(user_id, plan):
    tickets = get_user_tickets(user_id)
    max_per_day = FREE_MAX_MATCHES if plan == "free" else VIP_MAX_MATCHES
    today = datetime.utcnow().date()
    today_tickets = [t for t in tickets if datetime.fromisoformat(t[2]).date() == today]
    return len(today_tickets) < max_per_day

def create_ticket(user_id, match_ids, plan):
    if len(match_ids) > 5:
        match_ids = match_ids[:5]

    if not can_create_pronostic(user_id, plan):
        return {"text": f"⚠️ Hai già creato {FREE_MAX_MATCHES if plan=='free' else VIP_MAX_MATCHES} pronostici oggi!"}

    add_ticket(user_id, match_ids)
    total_today = len([t for t in get_user_tickets(user_id) if datetime.fromisoformat(t[2]).date() == datetime.utcnow().date()])
    return {"text": f"✅ Pronostico creato con {len(match_ids)} partite!\nPronostico numero {total_today} di oggi."}
