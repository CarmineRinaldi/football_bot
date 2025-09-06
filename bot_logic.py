from db import add_user, get_user_tickets, add_ticket, can_add_prediction
from football_api import get_leagues, get_matches, get_national_teams

def start(update, context):
    user_id = update["message"]["from"]["id"]
    add_user(user_id)
    return show_main_menu(update, context)

def show_main_menu(update, context):
    keyboard = [
        [{"text": "Free Plan 🆓", "callback_data": "plan_free"}],
        [{"text": "Le mie schedine 📋", "callback_data": "my_tickets"}]
    ]
    message = "Benvenuto! Scegli un piano o controlla le tue schedine:"
    return {"text": message, "reply_markup": {"inline_keyboard": keyboard}}

def show_plan_info(update, context, plan):
    text = ("🆓 **Free Plan**: puoi fare fino a 5 pronostici al giorno.\n"
            "Scegli tra Campionati o Nazionali e seleziona le partite per la tua schedina.")
    keyboard = [
        [{"text": "Scegli Campionato", "callback_data": "choose_league"}],
        [{"text": "Nazionali", "callback_data": "choose_national"}],
        [{"text": "🔙 Indietro", "callback_data": "main_menu"}]
    ]
    return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}

def show_leagues(update, context):
    leagues = get_leagues()
    keyboard = [[{"text": l["league"]["name"], "callback_data": f"league_{l['league']['id']}"}] for l in leagues[:20]]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "plan_free"}])
    return {"text": "Seleziona un campionato:", "reply_markup": {"inline_keyboard": keyboard}}

def show_national_teams(update, context):
    teams = get_national_teams()
    keyboard = [[{"text": t["name"], "callback_data": f"team_{t['id']}"}] for t in teams[:20]]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "plan_free"}])
    return {"text": "Seleziona una nazionale:", "reply_markup": {"inline_keyboard": keyboard}}

def show_matches(update, context, league_id):
    matches = get_matches(league_id)
    keyboard = [[{"text": f"{m['home']} vs {m['away']}", "callback_data": f"team_{m['id']}"}] for m in matches[:20]]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "choose_league"}])
    return {"text": "Seleziona le partite per la schedina:", "reply_markup": {"inline_keyboard": keyboard}}

def make_prediction(update, context, match_id):
    user_id = update["callback_query"]["from"]["id"]
    if not can_add_prediction(user_id):
        return {"text": "Hai già fatto 5 pronostici oggi. Riprova domani!"}

    add_ticket(user_id, [match_id])
    return {"text": f"Pronostico registrato! Puoi fare ancora {5 - len(get_user_tickets(user_id))} pronostici oggi."}
