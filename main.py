from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from bot_logic import start, show_main_menu, show_plan_info, send_message
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

        if cb_data == "back":
            show_main_menu(chat_id)
        elif cb_data == "plan_free":
            show_plan_info(chat_id, "free")
        elif cb_data == "plan_2eur":
            show_plan_info(chat_id, "2eur")
        elif cb_data == "plan_vip":
            show_plan_info(chat_id, "vip")
        else:
            send_message(chat_id, f"Callback ricevuto: {cb_data}")

    return JSONResponse(content={"ok": True})

@app.get("/")
async def root():
    return {"status": "Bot attivo"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
