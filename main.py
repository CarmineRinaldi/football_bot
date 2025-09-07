from fastapi import FastAPI, Request
from mine import start, handle_back, show_plan_info, show_search_choice, show_alphabet_keyboard, show_filtered_options, show_matches, search_team_prompt, show_search_results
from stripe_webhook import handle_stripe_event
import uvicorn

app = FastAPI()

# --------------------------
# Telegram Webhook
# --------------------------
@app.post("/webhook")
async def telegram_webhook(update: Request):
    data = await update.json()
    user_id = None

    # Gestione messaggi
    if "message" in data:
        user_id = data["message"]["from"]["id"]
        return start(data, {})

    # Gestione callback button
    elif "callback_query" in data:
        cb = data["callback_query"]
        user_id = cb["from"]["id"]
        cb_data = cb["data"]

        # Ritorna al menu principale
        if cb_data == "main_menu":
            return start({"message": {"from": {"id": user_id}}}, {})

        # Tasti di ritorno
        elif cb_data == "back":
            return handle_back(user_id, last_state=None)  # puoi gestire last_state con context se vuoi

        # Scelta piano
        elif cb_data.startswith("plan_"):
            plan = cb_data.split("_")[1]
            return show_plan_info(user_id, plan)

        # Selezione tipo campionato/nazionale
        elif cb_data.startswith("select_type_"):
            parts = cb_data.split("_")
            type_ = parts[2]  # league o national
            plan = parts[3]
            return show_search_choice(user_id, type_, plan)

        # Filtri alfabetici
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

        # Partite
        elif cb_data.startswith("league_") or cb_data.startswith("national_"):
            parts = cb_data.split("_")
            league_id = parts[1]
            plan = parts[2]
            return show_matches(user_id, league_id, plan)

        # Ricerca squadra
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
    return handle_stripe_event(payload, sig_header)

# --------------------------
# Root test
# --------------------------
@app.get("/")
async def root():
    return {"status": "Bot attivo"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
