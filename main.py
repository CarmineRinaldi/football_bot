# main.py
from fastapi import FastAPI, Request
import requests
import logging
import os

# -------------------------
# CONFIGURAZIONE BOT (da variabili d'ambiente)
# -------------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN")  # il token Telegram dal tuo env
BOT_URL = f"https://api.telegram.org/bot{TOKEN}"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # url completo del webhook dal tuo env

# -------------------------
# LOGGING
# -------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------
# APP FASTAPI
# -------------------------
app = FastAPI()

# -------------------------
# FUNZIONE PER IMPOSTARE IL WEBHOOK
# -------------------------
def set_webhook():
    if not TOKEN or not WEBHOOK_URL:
        logger.error("TOKEN o WEBHOOK_URL non impostati nelle variabili d'ambiente!")
        return
    response = requests.post(
        f"{BOT_URL}/setWebhook",
        params={"url": WEBHOOK_URL}
    )
    if response.status_code == 200:
        logger.info("Webhook impostato correttamente")
    else:
        logger.error(f"Errore impostando webhook: {response.text}")

# -------------------------
# ROTTA PRINCIPALE PER TEST
# -------------------------
@app.get("/")
async def root():
    return {"message": "Bot attivo e funzionante!"}

# -------------------------
# ROTTA PER WEBHOOK
# -------------------------
@app.post(f"/webhook/{TOKEN}")
async def telegram_webhook(request: Request):
    try:
        update = await request.json()
        logger.info(f"Aggiornamento ricevuto: {update}")

        # Esempio: invio risposta testuale al mittente
        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"].get("text", "")
            send_message(chat_id, f"Hai scritto: {text}")

        return {"ok": True}
    except Exception as e:
        logger.error(f"Errore gestione webhook: {e}")
        return {"ok": False, "error": str(e)}

# -------------------------
# FUNZIONE PER INVIO MESSAGGI
# -------------------------
def send_message(chat_id: int, text: str):
    try:
        response = requests.post(
            f"{BOT_URL}/sendMessage",
            data={"chat_id": chat_id, "text": text}
        )
        if response.status_code != 200:
            logger.error(f"Errore invio messaggio: {response.text}")
    except Exception as e:
        logger.error(f"Eccezione invio messaggio: {e}")

# -------------------------
# AVVIO DEL WEBHOOK ALL'AVVIO
# -------------------------
@app.on_event("startup")
async def startup_event():
    set_webhook()
    logger.info("Bot avviato correttamente e webhook impostato")
