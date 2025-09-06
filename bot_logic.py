from typing import Dict, Any
import json

# Campionati reali
LEAGUES = {
    "serie_a": "Serie A 🇮🇹",
    "premier": "Premier League 🏴",
    "laliga": "La Liga 🇪🇸",
    "bundesliga": "Bundesliga 🇩🇪",
    "ligue1": "Ligue 1 🇫🇷",
    "champions": "Champions League 🏆",
    "italy_nat": "Nazionale Italia 🇮🇹"
}

async def handle_update(update: Dict[str, Any]):
    if "message" in update and "text" in update["message"]:
        text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]
        return await start(chat_id)
    elif "callback_query" in update:
        data = update["callback_query"]["data"]
        chat_id = update["callback_query"]["message"]["chat"]["id"]
        return await handle_callback(chat_id, data)


async def start(chat_id):
    text = "🎉 Benvenuto nel tuo bot calcistico super divertente! ⚽\n" \
           "Scegli un piano e iniziamo a creare le tue schedine!"
    keyboard = [
        [{"text": "Free Plan 🆓", "callback_data": "plan_free"}],
        [{"text": "2€ Pack 💶", "callback_data": "plan_2eur"}],
        [{"text": "VIP Monthly 👑", "callback_data": "plan_vip"}],
        [{"text": "Le mie schedine 📋", "callback_data": "my_tickets"}]
    ]
    reply_markup = {"inline_keyboard": keyboard}
    return {"chat_id": chat_id, "text": text, "reply_markup": reply_markup}


async def handle_callback(chat_id, data):
    if data == "plan_free":
        return await show_plan_info(chat_id, "free")
    elif data == "plan_2eur":
        return await show_plan_info(chat_id, "2eur")
    elif data == "plan_vip":
        return await show_plan_info(chat_id, "vip")
    elif data == "my_tickets":
        return await show_my_tickets(chat_id)
    elif data.startswith("select_league_"):
        plan = data.split("_")[-1]
        return await show_leagues(chat_id, plan)
    elif data.startswith("league_"):
        league_id = data.split("_", 1)[1]
        return await show_matches(chat_id, league_id)
    elif data == "main_menu":
        return await start(chat_id)
    else:
        return {"chat_id": chat_id, "text": "Comando non riconosciuto!"}


async def show_plan_info(chat_id, plan):
    if plan == "free":
        text = "🆓 **Free Plan:** puoi creare fino a 5 partite per schedina. Scegli il tuo campionato preferito e divertiti!"
        keyboard = [
            [{"text": "Scegli Campionato ⚽", "callback_data": "select_league_free"}],
            [{"text": "🔙 Indietro", "callback_data": "main_menu"}]
        ]
    else:
        # Link di esempio Stripe
        text = f"💳 **{plan.upper()} Plan:** clicca per procedere al pagamento!"
        link = "https://buy.stripe.com/test_link"  # sostituire con link reale
        keyboard = [
            [{"text": f"Procedi a pagamento {plan.upper()}", "url": link}],
            [{"text": "🔙 Indietro", "callback_data": "main_menu"}]
        ]
    reply_markup = {"inline_keyboard": keyboard}
    return {"chat_id": chat_id, "text": text, "reply_markup": reply_markup}


async def show_leagues(chat_id, plan):
    text = "Seleziona il campionato che vuoi per la tua schedina:"
    keyboard = []
    for league_id, league_name in LEAGUES.items():
        keyboard.append([{"text": league_name, "callback_data": f"league_{league_id}"}])
    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"plan_{plan}"}])
    reply_markup = {"inline_keyboard": keyboard}
    return {"chat_id": chat_id, "text": text, "reply_markup": reply_markup}


async def show_matches(chat_id, league_id):
    text = f"Qui puoi scegliere le partite reali per {LEAGUES.get(league_id, league_id)} (esempio):"
    # qui si possono inserire le partite reali
    keyboard = [
        [{"text": "Partita 1", "callback_data": "match_1"}],
        [{"text": "Partita 2", "callback_data": "match_2"}],
        [{"text": "🔙 Indietro", "callback_data": "select_league_free"}]
    ]
    reply_markup = {"inline_keyboard": keyboard}
    return {"chat_id": chat_id, "text": text, "reply_markup": reply_markup}


async def show_my_tickets(chat_id):
    text = "📋 Le tue schedine salvate (esempio):\n- Schedina 1\n- Schedina 2"
    keyboard = [[{"text": "🔙 Indietro", "callback_data": "main_menu"}]]
    reply_markup = {"inline_keyboard": keyboard}
    return {"chat_id": chat_id, "text": text, "reply_markup": reply_markup}
