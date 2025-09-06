from db import add_user, get_user_plan, get_user_tickets, add_match_prediction, can_create_prediction, add_ticket
from football_api import get_leagues, get_matches

def start(update, context):
    user_id = update["message"]["from"]["id"]
    add_user(user_id)
    return show_main_menu(update, context)

def show_main_menu(update, context):
    keyboard = [
        [{"text": "Free Plan 🆓", "callback_data": "plan_free"}],
        [{"text": "Le mie schedine 📋", "callback_data": "my_tickets"}]
    ]
    message = ("Benvenuto! Scegli il Free Plan per creare fino a 5 pronostici al giorno.\n\n"
               "Clicca Free Plan per leggere la guida.")
    return {"text": message, "reply_markup": {"inline_keyboard": keyboard}}

def show_plan_info(update, context, plan):
    message = ("🆓 **Free Plan:** ogni giorno puoi creare fino a 5 pronostici.\n"
               "1️⃣ Seleziona 'Scegli campionato' o 'Nazioni'\n"
               "2️⃣ Scegli le partite reali\n"
               "3️⃣ Seleziona il pronostico 1/X/2\n"
               "4️⃣ Conferma la schedina")
    keyboard = [
        [{"text": "Scegli campionato o nazionali ⚽", "callback_data": f"select_league_{plan}"}],
        [{"text": "🔙 Indietro", "callback_data": "main_menu"}]
    ]
    return {"text": message, "reply_markup": {"inline_keyboard": keyboard}}

def show_leagues(update, context, plan):
    leagues = get_leagues()  # Campionati + Nazionali
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
    if add_match_prediction(user_id, match_id, prediction):
        return {"text": f"Pronostico salvato: {prediction}"}
    else:
        return {"text": "Hai già creato 5 pronostici oggi, riprova domani!"}

def create_ticket(user_id, match_ids):
    add_ticket(user_id, match_ids)
    return {"text": f"Schedina creata con {len(match_ids)} partite!"}

def show_user_tickets(update, context):
    user_id = update["message"]["from"]["id"]
    tickets = get_user_tickets(user_id)
    if not tickets:
        return {"text": "Non hai ancora schedine create."}
    text = "Le tue schedine:\n\n"
    for idx, t in enumerate(tickets, start=1):
        text += f"{idx}. Partite: {t['match_ids']} ({t['date_created']})\n"
    return {"text": text}
