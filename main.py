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
    context = {}

    if "message" in data:
        response = start(data, context)
        return JSONResponse(content=response)  # ✅ Converte in JSON valido
    elif "callback_query" in data:
        cb_data = data["callback_query"]["data"]
        if cb_data == "back":
            response = show_main_menu(data, context)
            return JSONResponse(content=response)
        return JSONResponse(content={"text": f"Callback ricevuto: {cb_data}"})

    return JSONResponse(content={"text": "Aggiornamento non gestito"})

@app.get("/")
async def root():
    return {"status": "Bot attivo"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
