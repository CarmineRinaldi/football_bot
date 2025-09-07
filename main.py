from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from bot_logic import start, show_main_menu
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
    
    # --------------------------
    # Messaggi
    # --------------------------
    if "message" in data:
        start(data, context={})  # ✅ Ora start invia direttamente il messaggio
        return JSONResponse(content={"status": "ok"})

    # --------------------------
    # Callback query
    # --------------------------
    elif "callback_query" in data:
        cb_data = data["callback_query"]["data"]

        if cb_data == "back":
            show_main_menu(data["callback_query"]["message"]["chat"]["id"])
            return JSONResponse(content={"status": "ok"})

        # Qui puoi gestire altri callback
        return JSONResponse(content={"status": "callback ricevuto", "data": cb_data})

    return JSONResponse(content={"status": "aggiornamento non gestito"})


@app.get("/")
async def root():
    return {"status": "Bot attivo"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
