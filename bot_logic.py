from db import add_user, get_user_plan, add_ticket, get_user_tickets
from football_api import get_leagues, get_national_teams, get_matches
from datetime import datetime
import string

# --------------------------
# Funzioni menu principale
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
        text = "🆓 **Free Plan:** puoi fare fino a 5 pronostici al giorno, massimo 5 partite per pronostico!"
    elif plan == "2eur":
        text = "💶 **2€ Pack:** più pronostici giornalieri e funzionalità extra!"
    else:
        text = "👑 **VIP:** massimo 5 pronostici al giorno, aggiornamenti e supporto VIP!"

    keyboard = [
        [{"text": "Scegli campionato ⚽", "callback_data": f"select_league_{plan}"}],
        [{"text": "Nazionali 🌍", "callback_data": f"select_national_{plan}"}],
        [{"text": "🔍 Ricerca 🔎", "callback_data": f"search_{plan}"}],
        [{"text": "🔙 Indietro", "callback_data": "main_menu"}]
    ]
    return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}


# --------------------------
# Funzioni campionati/nazionali paginati
# --------------------------

def paginate_items(items, page=0, per_page=10):
    total_pages = (len(items) + per_page - 1) // per_page
    page_items = items[page*per_page:(page+1)*per_page]
    return page_items, total_pages

def create_league_keyboard(leagues, page, total_pages, plan, prefix):
    keyboard = [[{"text": l["display_name"], "callback_data": f"{prefix}_{l['league']['id']}_{plan}"}] for l in leagues]
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append({"text": "⬅️ Indietro", "callback_data": f"{prefix}_page_{page-1}_{plan}"})
    if page < total_pages - 1:
        nav_buttons.append({"text": "➡️ Avanti", "callback_data": f"{prefix}_page_{page+1}_{plan}"})
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"plan_{plan}"}])
    return keyboard

def show_leagues(update, context, plan, page=0):
    leagues = get_leagues()
    if not leagues:
        return {"text": "😕 Nessun campionato disponibile.", "reply_markup": {"inline_keyboard": [[{"text": "🔙 Indietro", "callback_data": f"plan_{plan}"}]]}}

    page_items, total_pages = paginate_items(leagues, page)
    keyboard = create_league_keyboard(page_items, page, total_pages, plan, "league")
    return {"text": "🏟️ Seleziona un campionato (max 5 partite):", "reply_markup": {"inline_keyboard": keyboard}}

def show_nationals(update, context, plan, page=0):
    leagues = get_national_teams()
    if not leagues:
        return {"text": "🌍 Nessuna nazionale disponibile.", "reply_markup": {"inline_keyboard": [[{"text": "🔙 Indietro", "callback_data": f"plan_{plan}"}]]}}

    page_items, total_pages = paginate_items(leagues, page)
    keyboard = create_league_keyboard(page_items, page, total_pages, plan, "national")
    return {"text": "🌍 Seleziona una nazionale (max 5 partite):", "reply_markup": {"inline_keyboard": keyboard}}


# --------------------------
# Funzione ricerca
# --------------------------

def search_leagues(update, context, plan, query):
    all_leagues = get_leagues() + get_national_teams()
    results = [l for l in all_leagues if query.lower() in l["display_name"].lower()]

    if not results:
        return {"text": f"😕 Nessuna squadra o campionato trovato per '{query}'!", "reply_markup": {"inline_keyboard": [[{"text": "🔙 Indietro", "callback_data": f"plan_{plan}"}]]}}

    keyboard = [[{"text": l["display_name"], "callback_data": f"search_result_{l['league']['id']}_{plan}"}] for l in results[:20]]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"plan_{plan}"}])
    return {"text": f"🔎 Risultati per '{query}':", "reply_markup": {"inline_keyboard": keyboard}}


# --------------------------
# Funzioni partite
# --------------------------

def show_matches(update, context, league_id, plan):
    matches = get_matches(league_id)
    if not matches:
        return {"text": "⚽ Nessuna partita disponibile.", "reply_markup": {"inline_keyboard": [[{"text": "🔙 Indietro", "callback_data": f"select_league_{plan}"}]]}}

    keyboard = [[{"text": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}", "callback_data": f"match_{m['fixture']['id']}"}] for m in matches[:20]]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"select_league_{plan}"}])
    return {"text": "⚽ Seleziona fino a 5 partite per il pronostico giornaliero:", "reply_markup": {"inline_keyboard": keyboard}}


# --------------------------
# Funzioni pronostici
# --------------------------

def can_create_pronostic(user_id, max_per_day=5):
    tickets = get_user_tickets(user_id)
    today = datetime.utcnow().date()
    today_tickets = [t for t in tickets if datetime.fromisoformat(t[2]).date() == today]
    return len(today_tickets) < max_per_day

def create_ticket(user_id, match_ids):
    if len(match_ids) > 5:
        match_ids = match_ids[:5]

    if not can_create_pronostic(user_id):
        return {"text": "⚠️ Hai già creato 5 pronostici oggi!\nRiprova domani per nuove emozioni calcistiche ⚽🎯"}

    add_ticket(user_id, match_ids)
    total_today = len([t for t in get_user_tickets(user_id) if datetime.fromisoformat(t[2]).date() == datetime.utcnow().date()])
    return {"text": f"✅ Pronostico creato con {len(match_ids)} partite!\nPronostico numero {total_today} di oggi."}


# --------------------------
# GESTORE CALLBACK COMPLETO
# --------------------------

def handle_callback(callback_data, update, context):
    user_id = update["callback_query"]["from"]["id"]

    # Menu principale
    if callback_data == "main_menu":
        return show_main_menu(update, context)

    # Selezione piano
    if callback_data.startswith("plan_"):
        plan = callback_data.split("_")[1]
        return show_plan_info(update, context, plan)

    # Campionati paginati
    if callback_data.startswith("select_league_"):
        plan = callback_data.split("_")[-1]
        return show_leagues(update, context, plan)

    # Nazionali paginati
    if callback_data.startswith("select_national_"):
        plan = callback_data.split("_")[-1]
        return show_nationals(update, context, plan)

    # Pagine campionati/nazionali con sicurezza
    if "_page_" in callback_data:
        parts = callback_data.split("_")
        prefix = parts[0]
        try:
            page = int(parts[2])
        except ValueError:
            page = 0
        plan = parts[3]
        if prefix == "league":
            return show_leagues(update, context, plan, page)
        else:
            return show_nationals(update, context, plan, page)

    # Ricerca
    if callback_data.startswith("search_"):
        plan = callback_data.split("_")[1]
        return {"text": "Scrivi il nome della squadra o del campionato da cercare:"}

    # Risultati ricerca
    if callback_data.startswith("search_result_"):
        parts = callback_data.split("_")
        try:
            league_id = int(parts[2])
        except ValueError:
            league_id = 0
        plan = parts[3]
        return show_matches(update, context, league_id, plan)

    # Selezione partita
    if callback_data.startswith("match_"):
        match_id = callback_data.split("_")[1]
        return {"text": f"✅ Hai selezionato la partita {match_id}!"}
