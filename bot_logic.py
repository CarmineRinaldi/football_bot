from db import add_user, get_user_plan, add_ticket
from football_api import get_leagues, get_matches

def start(update, context):
    user_id = update["message"]["from"]["id"]
    add_user(user_id)
    return show_main_menu(update, context)

def show_main_menu(update, context):
    keyboard = [
        [{"text": "Free Plan", "callback_data": "plan_free"}],
        [{"text": "2€ Pack", "callback_data": "plan_2eur"}],
        [{"text": "VIP Monthly", "callback_data": "plan_vip"}],
        [{"text": "Le mie schedine", "callback_data": "my_tickets"}]
    ]
    message = "Benvenuto! Scegli un piano o controlla le tue schedine:"
    return {"text": message, "reply_markup": {"inline_keyboard": keyboard}}

def show_leagues(update, context):
    leagues = get_leagues()
    keyboard = [[{"text": l["league"]["name"], "callback_data": f"league_{l['league']['id']}"}] for l in leagues]
    keyboard.append([{"text": "Indietro", "callback_data": "main_menu"}])
    return {"text": "Seleziona un campionato:", "reply_markup": {"inline_keyboard": keyboard}}

def show_matches(update, context, league_id):
    matches = get_matches(league_id)
    keyboard = [[{"text": f"{m['fixture']['home']['name']} vs {m['fixture']['away']['name']}", 
                  "callback_data": f"match_{m['fixture']['id']}"}] for m in matches[:20]]
    keyboard.append([{"text": "Indietro", "callback_data": f"plan_{get_user_plan(update['message']['from']['id'])}"}])
    return {"text": "Seleziona le partite per la schedina:", "reply_markup": {"inline_keyboard": keyboard}}

def create_ticket(user_id, match_ids):
    from os import getenv
    plan = get_user_plan(user_id)
    free_max = int(getenv("FREE_MAX_MATCHES", 5))
    vip_max = int(getenv("VIP_MAX_MATCHES", 20))
    max_matches = vip_max if plan == "vip" else free_max if plan == "free" else len(match_ids)
    
    if len(match_ids) > max_matches:
        match_ids = match_ids[:max_matches]
    
    add_ticket(user_id, match_ids)
    return {"text": f"Schedina creata con {len(match_ids)} partite!"}
