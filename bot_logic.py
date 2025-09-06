from db import add_user, get_user_plan, add_ticket, get_user_tickets
from football_api import get_leagues, get_matches
import os

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
    message = "🎉 Benvenuto nel tuo bot calcistico super divertente! ⚽\nScegli un piano e iniziamo a creare le tue schedine!"
    return {"text": message, "reply_markup": {"inline_keyboard": keyboard}}

def show_plan_info(update, context, plan):
    if plan == "free":
        text = "🆓 **Free Plan:** puoi creare fino a 5 partite per schedina. Scegli il tuo campionato preferito e divertiti!"
        keyboard = [
            [{"text": "Scegli Campionato ⚽", "callback_data": f"select_league_{plan}"}],
            [{"text": "🔙 Indietro", "callback_data": "main_menu"}]
        ]
    elif plan == "2eur":
        stripe_link = os.getenv("STRIPE_PRICE_2EUR_LINK", "https://buy.stripe.com/2eur")
        text = f"💶 **2€ Pack:** più partite disponibili e accesso extra! Clicca sotto per attivare il piano."
        keyboard = [
            [{"text": "Acquista 2€ Pack 💶", "url": stripe_link}],
            [{"text": "🔙 Indietro", "callback_data": "main_menu"}]
        ]
    else:
        stripe_link = os.getenv("STRIPE_PRICE_VIP_LINK", "https://buy.stripe.com/vip")
        text = f"👑 **VIP:** massimo 20 partite per schedina, aggiornamenti premium e supporto VIP!"
        keyboard = [
            [{"text": "Acquista VIP 👑", "url": stripe_link}],
            [{"text": "🔙 Indietro", "callback_data": "main_menu"}]
        ]

    return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}

def show_leagues(update, context, plan):
    leagues = get_leagues()
    keyboard = [[{"text": l["league"]["name"], "callback_data": f"league_{l['league']['id']}_{plan}"}] for l in leagues[:30]]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"plan_{plan}"}])
    return {"text": "Seleziona il campionato che vuoi per la tua schedina:", "reply_markup": {"inline_keyboard": keyboard}}

def show_matches(update, context, league_id, plan):
    matches = get_matches(league_id)
    keyboard = [[{"text": f"{m['fixture']['home']['name']} vs {m['fixture']['away']['name']}", 
                  "callback_data": f"match_{m['fixture']['id']}"}] for m in matches[:20]]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"select_league_{plan}"}])
    return {"text": "Seleziona le partite per la schedina:", "reply_markup": {"inline_keyboard": keyboard}}

def create_ticket(user_id, match_ids):
    if len(match_ids) > 5 and get_user_plan(user_id) == "free":
        match_ids = match_ids[:5]
    add_ticket(user_id, match_ids)
    return {"text": f"Schedina creata con {len(match_ids)} partite!"}

def show_my_tickets(update, context):
    user_id = update["callback_query"]["from"]["id"]
    tickets = get_user_tickets(user_id)
    if not tickets:
        return {"text": "📭 Non hai ancora schedine!", "reply_markup": {"inline_keyboard":[[{"text": "🔙 Indietro", "callback_data": "main_menu"}]]}}
    text = "📋 Le tue schedine:\n\n"
    for t in tickets:
        text += f"- ID {t[0]}: {t[1]} (creata {t[2]})\n"
    keyboard = [[{"text": "🔙 Indietro", "callback_data": "main_menu"}]]
    return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}
