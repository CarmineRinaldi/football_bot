from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mine import start, show_main_menu, show_plan_info, handle_back, show_search_choice, show_alphabet_keyboard, show_filtered_options, show_matches, search_team_prompt, show_search_results
from stripe_webhook import handle_stripe_event
import uvicorn

app = FastAPI()

# --------------------------
# Telegram Webhook
# --------------------------
@app.post("/webhook")
async def telegram_webhook(update: Request):
    data = await update.json()
    context = {}
    try:
        # Messaggio normale
        if "message" in data:
            res = start(data, context)
            return JSONResponse(res)

        # Callback inline
        elif "callback_query" in data:
            cb_data = data["callback_query"]["data"]

            # Gestione tasto "back"
            if cb_data == "back":
                res = handle_back(data, context, context.get("last_state"))
                return JSONResponse(res)

            # Piani
            elif cb_data.startswith("plan_"):
                plan = cb_data.replace("plan_", "")
                res = show_plan_info(data, context, plan)
                context["current_plan"] = plan
                context["last_state"] = "plan_info"
                return JSONResponse(res)

            # Scelta ricerca
            elif cb_data.startswith("search_letter_") or cb_data.startswith("search_name_"):
                parts = cb_data.split("_")
                type_ = parts[2]
                plan = parts[3]
                res = show_search_choice(type_, plan)
                return JSONResponse(res)

            # Filtri alfabetici
            elif cb_data.startswith("filter_"):
                parts = cb_data.split("_")
                type_ = parts[1]
                letter = parts[2]
                plan = parts[3]
                res = show_filtered_options(type_, letter, plan)
                return JSONResponse(res)

            # Selezione partite
            elif cb_data.startswith("select_") or cb_data.startswith("match_"):
                # qui puoi aggiungere logica per selezionare partite e registrarle
                return JSONResponse({"text": f"Selezione: {cb_data}"})

            return JSONResponse({"text": f"Callback ricevuto: {cb_data}"})

        return JSONResponse({"text": "Aggiornamento non gestito"})
    
    except Exception as e:
        return JSONResponse({"error": str(e)})

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
