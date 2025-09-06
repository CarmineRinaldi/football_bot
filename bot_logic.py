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
        text = "🆓 **Free Plan:** fino a 5 partite per schedina."
    elif plan == "2eur":
        text = "💶 **2€ Pack:** più partite disponibili, funzionalità extra!"
    else:
        text = "👑 **VIP:** massimo 20 partite, aggiornamenti e supporto VIP."

    keyboard = [
        [{"text": "Scegli campionato ⚽", "callback_data": f"select_league_{plan}"}],
        [{"text": "🔙 Indietro", "callback_data": "main_menu"}]
    ]
    return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}

def show_leagues(update, context, plan):
    leagues = get_leagues()  # Nazionali + campionati
    keyboard = [[{"text": l["name"], "callback_data": f"league_{l['id']}_{plan}"}] for l in leagues[:20]]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"plan_{plan}"}])
    return {"text": "Seleziona un campionato o una nazionale:", "reply_markup": {"inline_keyboard": keyboard}}

def show_matches(update, context, league_id, plan):
    matches = get_matches(league_id)
    keyboard = []
    for m in matches[:20]:
        keyboard.append([
            {"text": "1", "callback_data": f"predict_{m['fixture']['id']}_home"},
            {"text": "X", "callback_data": f"predict_{m['fixture']['id']}_draw"},
            {"text": "2", "callback_data": f"predict_{m['fixture']['id']}_away"}
        ])
    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"select_league_{plan}"}])
    keyboard.append([{"text": "✅ Conferma schedina", "callback_data": f"confirm_ticket_{plan}"}])
    return {"text": "Seleziona i pronostici per le partite:", "reply_markup": {"inline_keyboard": keyboard}}

def save_prediction(user_id, match_id, prediction):
    add_match_prediction(user_id, match_id, prediction)
    return {"text": f"Pronostico salvato: {prediction}"}

def create_ticket(user_id, match_ids):
    plan = get_user_plan(user_id)
    if len(match_ids) > 5 and plan == "free":
        match_ids = match_ids[:5]
    add_ticket(user_id, match_ids)
    return {"text": f"Schedina creata con {len(match_ids)} partite!"}

def show_user_tickets(update, context):
    user_id = update["message"]["from"]["id"]
    tickets = get_user_tickets(user_id)
    if not tickets:
        return {"text": "Non hai ancora schedine create."}
    text = "Le tue schedine:\n\n"
    for idx, t in enumerate(tickets, start=1):
        text += f"{idx}. Partite: {t['match_ids']}\n"
    return {"text": text}
