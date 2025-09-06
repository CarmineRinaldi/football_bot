from db import add_user, get_user_plan, add_ticket, get_user_tickets, add_match_prediction
from football_api import get_leagues, get_matches

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
        text = "🆓 **Free Plan:** puoi creare fino a 5 partite per schedina."
    elif plan == "2eur":
        text = "💶 **2€ Pack:** più partite disponibili, accesso a funzionalità extra!"
    else:
        text = "👑 **VIP:** massimo 20 partite per schedina, aggiornamenti e supporto VIP."

    keyboard = [
        [{"text": "Scegli campionato ⚽", "callback_data": f"select_league_{plan}"}],
        [{"text": "🔙 Indietro", "callback_data": "main_menu"}]
    ]
    return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}

def show_leagues(update, context, plan):
    leagues = get_leagues()
    # aggiungi le nazionali manualmente
    national_teams = [
        {"league": {"id": 1001, "name": "Italia"}}, 
        {"league": {"id": 1002, "name": "Inghilterra"}},
        {"league": {"id": 1003, "name": "Germania"}}
    ]
    leagues = leagues[:20] + national_teams

    keyboard = [[{"text": l["league"]["name"], "callback_data": f"league_{l['league']['id']}_{plan}"}] for l in leagues]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"plan_{plan}"}])
    return {"text": "Seleziona un campionato:", "reply_markup": {"inline_keyboard": keyboard}}

def show_matches(update, context, league_id, plan):
    matches = get_matches(league_id)
    keyboard = [[{"text": f"{m['fixture']['home']['name']} vs {m['fixture']['away']['name']}", 
                  "callback_data": f"match_{m['fixture']['id']}_{plan}"}] for m in matches[:20]]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"select_league_{plan}"}])
    return {"text": "Seleziona le partite per la schedina:", "reply_markup": {"inline_keyboard": keyboard}}

def show_match_options(update, context, match_id, plan):
    # Mostra pulsanti 1 / X / 2 per la partita selezionata
    keyboard = [
        [{"text": "1️⃣ Casa", "callback_data": f"predict_{match_id}_1_{plan}"}],
        [{"text": "❌ Pareggio", "callback_data": f"predict_{match_id}_X_{plan}"}],
        [{"text": "2️⃣ Ospite", "callback_data": f"predict_{match_id}_2_{plan}"}],
        [{"text": "🔙 Indietro", "callback_data": f"league_back_{plan}"}]
    ]
    return {"text": "Scegli il pronostico per questa partita:", "reply_markup": {"inline_keyboard": keyboard}}

def save_prediction(user_id, match_id, prediction):
    add_match_prediction(user_id, match_id, prediction)
    return {"text": f"Pronostico salvato: {prediction}"}

def create_ticket(user_id, match_ids):
    if len(match_ids) > 5 and get_user_plan(user_id) == "free":
        match_ids = match_ids[:5]
    add_ticket(user_id, match_ids)
    return {"text": f"Schedina creata con {len(match_ids)} partite!"}
