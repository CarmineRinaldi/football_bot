from fastapi import FastAPI, Request
from db import add_user, get_user_plan, add_ticket, get_user_tickets
from football_api import get_leagues, get_national_teams, get_matches, search_teams, filter_by_letter
from datetime import datetime
import os
import uvicorn

FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))

app = FastAPI()

# --------------------------
# Funzioni del bot
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

def show_plan_info(user_id, plan):
    if plan == "free":
        text = f"🆓 **Free Plan:** puoi fare fino a {FREE_MAX_MATCHES} pronostici al giorno, massimo 5 partite per pronostico!"
    elif plan == "2eur":
        text = "💶 **2€ Pack:** più pronostici giornalieri e funzionalità extra!"
    else:
        text = f"👑 **VIP:** massimo {VIP_MAX_MATCHES} pronostici al giorno, aggiornamenti e supporto VIP!"

    keyboard = [
        [{"text": "Campionati ⚽", "callback_data": f"select_type_league_{plan}"}],
        [{"text": "Nazionali 🌍", "callback_data": f"select_type_national_{plan}"}],
        [{"text": "Cerca squadra 🔎", "callback_data": f"search_team_{plan}"}],
        [{"text": "🏟️ Menù principale calcistico", "callback_data": "main_menu"}]
    ]
    return {"text": text, "reply_markup": {"inline_keyboard": keyboard}}

def show_search_choice(user_id, type_, plan):
    tipo_testo = "campionato" if type_ == "league" else "nazionale"
    keyboard = [
        [{"text": "Per lettera 🔤", "callback_data": f"search_letter_{type_}_{plan}"}],
        [{"text": "Per nome 🔎", "callback_data": f"search_name_{type_}_{plan}"}],
        [{"text": "🔙 Indietro", "callback_data": "back"}],
        [{"text": "🏟️ Menù principale calcistico", "callback_data": "main_menu"}]
    ]
    return {"text": f"🔍 Scegli come cercare il {tipo_testo}:", "reply_markup": {"inline_keyboard": keyboard}}

def show_alphabet_keyboard(user_id, plan, type_):
    keyboard = [[{"text": c, "callback_data": f"filter_{type_}_{c}_{plan}"}] for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    tipo_testo = "campionato" if type_ == "league" else "nazionale"
    return {"text": f"🔤 Filtra per lettera iniziale del {tipo_testo}:", "reply_markup": {"inline_keyboard": keyboard}}

def show_filtered_options(user_id, type_, letter, plan):
    items = get_leagues() if type_ == "league" else get_national_teams()
    filtered = filter_by_letter(items, "display_name", letter)

    if not filtered:
        return {
            "text": f"😕 Nessun {type_} trovato con la lettera '{letter}'.",
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 Indietro", "callback_data": "back"}]]}
        }

    keyboard = [[{"text": o["display_name"], "callback_data": f"{type_}_{o['league']['id']}_{plan}"}] for o in filtered]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    return {"text": f"🏟️ Seleziona {type_}:", "reply_markup": {"inline_keyboard": keyboard}}

def show_matches(user_id, league_id, plan):
    matches = get_matches(league_id)
    if not matches:
        return {
            "text": "⚽ Nessuna partita disponibile per questa competizione!",
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 Indietro", "callback_data": "back"}]]}
        }

    keyboard = [[{"text": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}",
                  "callback_data": f"match_{m['fixture']['id']}_{plan}"}] for m in matches]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    return {
        "text": "⚽ Seleziona fino a 5 partite per il pronostico giornaliero:",
        "reply_markup": {"inline_keyboard": keyboard}
    }

def search_team_prompt(user_id, plan):
    return {"text": "🔎 Scrivi il nome della squadra che vuoi cercare:", "reply_markup": None}

def show_search_results(query, plan, type_=None):
    results = search_teams(query, type_)
    if not results:
        return {
            "text": f"😕 Nessun risultato trovato per '{query}'.",
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 Indietro", "callback_data": "back"}]]}
        }

    keyboard = [[{"text": r["team"], "callback_data": f"team_{r['match_id']}_{plan}"}] for r in results]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "back"}])
    return {"text": f"🔍 Risultati per '{query}':", "reply_markup": {"inline_keyboard": keyboard}}

def handle_back(user_id, last_state):
    # Torna al menu principale per ora
    return show_main_menu({"message": {"from": {"id": user_id}}}, {})


# --------------------------
# FastAPI Webhook
# --------------------------
@app.post("/webhook")
async def telegram_webhook(update: Request):
    data = await update.json()

    # Messaggi
    if "message" in data:
        return start(data, {})

    # Callback button
    elif "callback_query" in data:
        cb = data["callback_query"]
        user_id = cb["from"]["id"]
        cb_data = cb["data"]

        if cb_data == "main_menu":
            return start({"message": {"from": {"id": user_id}}}, {})
        elif cb_data == "back":
            return handle_back(user_id, last_state=None)
        elif cb_data.startswith("plan_"):
            plan = cb_data.split("_")[1]
            return show_plan_info(user_id, plan)
        elif cb_data.startswith("select_type_"):
            parts = cb_data.split("_")
            type_ = parts[2]
            plan = parts[3]
            return show_search_choice(user_id, type_, plan)
        elif cb_data.startswith("search_letter_"):
            parts = cb_data.split("_")
            type_ = parts[2]
            plan = parts[3]
            return show_alphabet_keyboard(user_id, plan, type_)
        elif cb_data.startswith("filter_"):
            parts = cb_data.split("_")
            type_ = parts[1]
            letter = parts[2]
            plan = parts[3]
            return show_filtered_options(user_id, type_, letter, plan)
        elif cb_data.startswith("league_") or cb_data.startswith("national_"):
            parts = cb_data.split("_")
            league_id = parts[1]
            plan = parts[2]
            return show_matches(user_id, league_id, plan)
        elif cb_data.startswith("search_team_"):
            plan = cb_data.split("_")[2]
            return search_team_prompt(user_id, plan)

    return {"status": "ignored"}


# --------------------------
# Stripe Webhook
# --------------------------
@app.post("/stripe-webhook")
async def stripe_webhook(req: Request):
    payload = await req.body()
    sig_header = req.headers.get("stripe-signature")
    from stripe_webhook import handle_stripe_event
    return handle_stripe_event(payload, sig_header)


# --------------------------
# Root test
# --------------------------
@app.get("/")
async def root():
    return {"status": "Bot attivo"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
