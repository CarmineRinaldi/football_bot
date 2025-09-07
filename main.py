from fastapi import FastAPI, Request
from bot_logic import start, show_main_menu
import uvicorn

app = FastAPI()

# --------------------------
# Webhook Handler
# --------------------------
@app.post("/webhook")
async def telegram_webhook(update: Request):
    data = await update.json()
    context = {}
    if "message" in data:
        return start(data, context)
    elif "callback_query" in data:
        cb_data = data["callback_query"]["data"]
        if cb_data == "back":
            return show_main_menu(data, context)
        return {"text": f"Callback ricevuto: {cb_data}"}
    return {"text": "Aggiornamento non gestito"}

@app.get("/")
async def root():
    return {"status": "Bot attivo"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
