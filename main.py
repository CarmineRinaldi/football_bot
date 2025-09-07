from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from bot_logic import (
    start, show_main_menu, show_plan_info,
    show_search_choice, show_alphabet_keyboard,
    show_filtered_options, show_matches,
    search_team_prompt, show_search_results,
    send_message, delete_message
)
from db import init_db
import uvicorn
import os
import requests

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
        msg_id = data["callback_query"]["message"]["message_id"]

        # 🔙 Indietro
        if cb_data == "back":
            delete_message(chat_id, msg_id)
            show_main_menu(chat_id)

        # 📋 Piani
        elif cb_data == "plan_free":
            show_plan_info(chat_id, "free", old_msg_id=msg_id)
        elif cb_data == "plan_2eur":
            show_plan_info(chat_id, "2eur", old_msg_id=msg_id)
        elif cb_data == "plan_vip":
            show_plan_info(chat_id, "vip", old_msg_id=msg_id)

        # ⚽ Campionati / 🌍 Nazionali / 🔎 Squadre
        elif cb_data.startswith("select_type_"):
            _, type_, plan = cb_data.split("_", 2)
            show_search_choice(chat_id, type_, plan, old_msg_id=msg_id)

        elif cb_data.startswith("search_letter_"):
            _, _, type_, plan = cb_data.split("_", 3)
            show_alphabet_keyboard(chat_id, plan, type_, old_msg_id=msg_id)

        elif cb_data.startswith("filter_"):
            _, type_, letter, plan = cb_data.split("_", 3)
            show_filtered_options(chat_id, type_, letter, plan, old_msg_id=msg_id)

        elif cb_data.startswith("search_team_"):
            _, _, plan = cb_data.split("_", 2)
            search_team_prompt(chat_id, plan, old_msg_id=msg_id)

        elif cb_data.startswith("match_"):
            _, match_id, plan = cb_data.split("_", 2)
            delete_message(chat_id, msg_id)
            send_message(chat_id, f"📌 Hai selezionato la partita con ID {match_id} (Piano: {plan})")

        elif cb_data.startswith("team_"):
            _, team_id, plan = cb_data.split("_", 2)
            delete_message(chat_id, msg_id)
            send_message(chat_id, f"📌 Hai selezionato la squadra con ID {team_id} (Piano: {plan})")

        # Default
        else:
            delete_message(chat_id, msg_id)
            send_message(chat_id, f"⚠️ Callback non gestito: {cb_data}")

    return JSONResponse(content={"ok": True})


# --------------------------
# Root
# --------------------------
@app.get("/")
async def root():
    return {"status": "Bot attivo"}


# --------------------------
# Test connessione Telegram
# --------------------------
@app.get("/test_telegram")
async def test_telegram():
    try:
        token = os.getenv("TG_BOT_TOKEN")
        if not token:
            return {"success": False, "error": "Variabile TG_BOT_TOKEN non trovata"}

        url = f"https://api.telegram.org/bot{token}/getMe"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return {"success": True, "data": res.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
