from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from bot_logic import (
    start, show_main_menu, show_plan_info,
    show_search_choice, show_alphabet_keyboard,
    show_filtered_options, show_matches,
    search_team_prompt, show_search_results,
    send_message
)
from db import init_db
import uvicorn

app = FastAPI()

# --------------------------
# Inizializza DB all'avvio
# --------------------------
init_db()

# --------------------------
# Webhook Handler
# --------------------------
@app.post("/webhook")
async def telegram_webhook(update: Request):
    data = await update.json()
    context = {}

    if "message" in data:
        start(data, context)

    elif "callback_query" in data:
        cb_data = data["callback_query"]["data"]
        chat_id = data["callback_query"]["message"]["chat"]["id"]

        # 🔙 Indietro
        if cb_data == "back":
            show_main_menu(chat_id)

        # 📋 Piani
        elif cb_data == "plan_free":
            show_plan_info(chat_id, "free")
        elif cb_data == "plan_2eur":
            show_plan_info(chat_id, "2eur")
        elif cb_data == "plan_vip":
            show_plan_info(chat_id, "vip")

        # ⚽ Campionati / 🌍 Nazionali / 🔎 Squadre
        elif cb_data.startswith("select_type_"):
            _, type_, plan = cb_data.split("_", 2)
            show_search_choice(chat_id, type_, plan)

        elif cb_data.startswith("search_letter_"):
            _, _, type_, plan = cb_data.split("_", 3)
            show_alphabet_keyboard(chat_id, plan, type_)

        elif cb_data.startswith("filter_"):
            _, type_, letter, plan = cb_data.split("_", 3)
            show_filtered_options(chat_id, type_, letter, plan)

        elif cb_data.startswith("search_team_"):
            _, _, plan = cb_data.split("_", 2)
            search_team_prompt(chat_id, plan)

        elif cb_data.startswith("match_"):
            _, match_id, plan = cb_data.split("_", 2)
            send_message(chat_id, f"📌 Hai selezionato la partita con ID {match_id} (Piano: {plan})")

        elif cb_data.startswith("team_"):
            _, team_id, plan = cb_data.split("_", 2)
            send_message(chat_id, f"📌 Hai selezionato la squadra con ID {team_id} (Piano: {plan})")

        # Default
        else:
            send_message(chat_id, f"⚠️ Callback non gestito: {cb_data}")

    return JSONResponse(content={"ok": True})

@app.get("/")
async def root():
    return {"status": "Bot attivo"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
