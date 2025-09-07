from fastapi import FastAPI, Request
from db import init_db
from bot_logic import start, show_main_menu, send_message
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

    # ----------------------
    # Messaggio standard
    # ----------------------
    if "message" in data:
        start(data, {})  # il bot invia messaggi con send_message
        return {"ok": True}

    # ----------------------
    # Callback inline
    # ----------------------
    elif "callback_query" in data:
        cb = data["callback_query"]
        cb_data = cb["data"]
        chat_id = cb["message"]["chat"]["id"]

        # Bottone "Indietro"
        if cb_data == "back":
            show_main_menu(chat_id)
        # Puoi aggiungere altri callback qui
        else:
            send_message(chat_id, f"Callback ricevuto: {cb_data}")

        # Rispondi sempre a Telegram per chiudere il "loading" del bottone
        return {"ok": True}

    # ----------------------
    # Aggiornamento non gestito
    # ----------------------
    return {"ok": True}


@app.get("/")
async def root():
    return {"status": "Bot attivo"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
