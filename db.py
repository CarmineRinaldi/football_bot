# bot_logic.py
from db import add_user, get_user_plan, add_ticket, get_user_tickets, add_match_prediction
from football_api import get_leagues, get_matches, get_national_teams

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
    message = "Benvenuto! Scegli un piano o controlla le tue schedine:"
    return {"text": message, "reply_markup": {"inline_keyboard": keyboard}}

def show_plan_info(update, context, plan):
    if plan == "free":
        text = "🆓 Free Plan: puoi creare fino a 5 partite per schedina."
    elif plan == "2eur":
        text = "💶 2€ Pack: più partite disponibili, funzionalità extra!"
    else:
        text = "👑 VIP: massimo 20 partite per schedina, aggiornamenti VIP."
    
    keyboard = [
        [{"text": "Scegli campionato ⚽", "callback_data": f"select_league_{plan}"}],
        [{"text": "Scegli nazionale 🌍", "callback_data": f"select_national_{plan}"}],
        [{"text": "🔙 Indietro", "callback_data": "main_menu"}]
    ]
    return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}

def show_leagues(update, context, plan):
    leagues = get_leagues()
    keyboard = [[{"text": l["league"]["name"], "callback_data": f"league_{l['league']['id']}_{plan}"}] for l in leagues[:20]]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"plan_{plan}"}])
    return {"text": "Seleziona un campionato:", "reply_markup": {"inline_keyboard": keyboard}}

def show_national_teams(update, context, plan):
    teams = get_national_teams()
    keyboard = [[{"text": t["name"], "callback_data": f"national_{t['id']}_{plan}"}] for t in teams[:20]]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"plan_{plan}"}])
    return {"text": "Seleziona una nazionale:", "reply_markup": {"inline_keyboard": keyboard}}

def show_matches(update, context, league_id, plan):
    matches = get_matches(league_id)
    keyboard = []
    for m in matches[:20]:
        match_id = m['fixture']['id']
        text = f"{m['fixture']['home']['name']} vs {m['fixture']['away']['name']}"
        keyboard.append([{"text": text, "callback_data": f"match_{match_id}_{plan}"}])
    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"select_league_{plan}"}])
    return {"text": "Seleziona le partite per la schedina:", "reply_markup": {"inline_keyboard": keyboard}}

def show_match_options(update, context, match_id, plan):
    keyboard = [
        [{"text": "1️⃣ Vittoria casa", "callback_data": f"pred_{match_id}_1"}],
        [{"text": "❌ Pareggio", "callback_data": f"pred_{match_id}_X"}],
        [{"text": "2️⃣ Vittoria ospite", "callback_data": f"pred_{match_id}_2"}],
        [{"text": "🔙 Indietro", "callback_data": f"select_league_{plan}"}]
    ]
    return {"text": "Seleziona il pronostico:", "reply_markup": {"inline_keyboard": keyboard}}

def save_prediction(update, context, match_id, prediction):
    user_id = update["callback_query"]["from"]["id"]
    add_match_prediction(user_id, match_id, prediction)
    return {"text": f"Pronostico salvato: {prediction}"}
