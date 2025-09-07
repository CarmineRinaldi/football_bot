from db import add_user, get_user_plan, add_ticket, get_user_tickets
from football_api import get_leagues, get_national_teams, get_matches
from datetime import datetime

# Contesto per ricerca e paginazione {user_id: {"type": "league/national", "letter": "A", "plan": "free", "page": 0}}
user_context = {}

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
        [{"text": "🔙 Indietro", "callback_data": "main_menu"}]
    ]
    return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}

# --------------------------
# Funzioni campionati e nazionali con paginazione
# --------------------------

def paginate_items(items, page=0, per_page=10):
    total = len(items)
    pages = (total // per_page) + (1 if total % per_page else 0)
    start = page * per_page
    end = start + per_page
    return items[start:end], pages

def build_keyboard_with_pages(items, callback_prefix, page, plan, per_page=10):
    paged_items, total_pages = paginate_items(items, page, per_page)
    keyboard = [[{"text": i["display_name"], "callback_data": f"{callback_prefix}_{i['league']['id']}_{plan}"}] for i in paged_items]

    nav_row = []
    if page > 0:
        nav_row.append({"text": "⬅️ Indietro", "callback_data": f"{callback_prefix}_page_{page-1}_{plan}"})
    if page < total_pages - 1:
        nav_row.append({"text": "➡️ Avanti", "callback_data": f"{callback_prefix}_page_{page+1}_{plan}"})
    if nav_row:
        keyboard.append(nav_row)

    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"plan_{plan}"}])
    return keyboard

def show_leagues(update, context, plan, page=0):
    leagues = get_leagues()
    if not leagues:
        return {
            "text": "😕 Al momento non ci sono campionati disponibili.\nForse le squadre stanno facendo il riscaldamento... riprova più tardi!",
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 Indietro", "callback_data": f"plan_{plan}"}]]}
        }
    keyboard = build_keyboard_with_pages(leagues, "league", page, plan)
    return {"text": "🏟️ Seleziona un campionato e costruisci il tuo pronostico (max 5 partite):",
            "reply_markup": {"inline_keyboard": keyboard}}

def show_nationals(update, context, plan, page=0):
    nationals = get_national_teams()
    if not nationals:
        return {
            "text": "🌍 Nessuna nazionale in campo al momento!\nLe squadre staranno cantando l'inno... riprova più tardi!",
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 Indietro", "callback_data": f"plan_{plan}"}]]}
        }
    keyboard = build_keyboard_with_pages(nationals, "national", page, plan)
    return {"text": "🌍 Seleziona una nazionale e crea il tuo pronostico (max 5 partite):",
            "reply_markup": {"inline_keyboard": keyboard}}

# --------------------------
# Funzioni partite
# --------------------------

def show_matches(update, context, league_id, plan):
    matches = get_matches(league_id)
    if not matches:
        return {
            "text": "⚽ Nessuna partita disponibile per questa competizione!\nI giocatori forse sono negli spogliatoi... riprova più tardi!",
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 Indietro", "callback_data": f"select_league_{plan}"}]]}
        }
    keyboard = [[{"text": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}", 
                  "callback_data": f"match_{m['fixture']['id']}"}] for m in matches[:20]]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"select_league_{plan}"}])
    return {"text": "⚽ Seleziona fino a 5 partite per il pronostico giornaliero:",
            "reply_markup": {"inline_keyboard": keyboard}}

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
