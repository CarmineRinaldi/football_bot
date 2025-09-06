from db import add_user, get_user_plan, add_ticket, get_user_tickets
from football_api import get_leagues, get_matches

def start(update, context):
    user_id = update["message"]["from"]["id"]
    add_user(user_id)
    return show_main_menu(update, context)

def show_main_menu(update, context):
    keyboard = [
        [{"text": "🆓 Free Plan", "callback_data": "plan_free"}],
        [{"text": "💶 2€ Pack", "callback_data": "plan_2eur"}],
        [{"text": "👑 VIP Mensile", "callback_data": "plan_vip"}],
        [{"text": "📋 Le mie schedine", "callback_data": "my_tickets"}]
    ]
    message = "🎉 Benvenuto nel Bot Schedine Calcio! ⚽\nScegli il tuo piano o controlla le tue schedine:"
    return {"text": message, "reply_markup": {"inline_keyboard": keyboard}}

def show_plan_info(update, context, plan):
    if plan == "free":
        message = (
            "🆓 *Free Plan*\n"
            "Puoi selezionare fino a 5 partite per la tua schedina.\n"
            "Perfetto per provare il bot senza pagare nulla!"
        )
    elif plan == "2eur":
        message = (
            "💶 *2€ Pack*\n"
            "Puoi selezionare fino a 10 partite per schedina.\n"
            "Pagamento una tantum di 2€ per aumentare le tue possibilità!"
        )
    elif plan == "vip":
        message = (
            "👑 *VIP Mensile*\n"
            "Puoi selezionare fino a 20 partite per schedina.\n"
            "Accesso completo, aggiornamenti esclusivi e molto altro!"
        )
    keyboard = [
        [{"text": "⚽ Seleziona Campionato", "callback_data": f"select_league_{plan}"}],
        [{"text": "🔙 Indietro", "callback_data": "main_menu"}]
    ]
    return {"text": message, "reply_markup": {"inline_keyboard": keyboard}}

def show_leagues(update, context, plan):
    leagues = get_leagues()
    keyboard = [
        [{"text": f"{l['league']['name']} {l['country']['flag']}", "callback_data": f"league_{l['league']['id']}_{plan}"}]
        for l in leagues[:20]
    ]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": f"p_]()
