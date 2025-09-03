from flask import Flask, request, jsonify
import os
import telebot
import logging
import requests
from db import init_db, add_user, get_all_users
from bot_logic import send_daily_to_user
from payments import handle_stripe_webhook

# --- Config logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Variabili d'ambiente ---
TOKEN = os.environ.get("TG_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
ADMIN_TOKEN = os.environ.get("ADMIN_HTTP_TOKEN", "metti_un_token_lungo")
API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY")  # Inserisci qui la tua chiave API
API_FOOTBALL_URL = "https://v3.football.api-sports.io"

if not TOKEN or not WEBHOOK_URL or not API_FOOTBALL_KEY:
    logger.error("Variabili TG_BOT_TOKEN, WEBHOOK_URL o API_FOOTBALL_KEY mancanti!")
    exit(1)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- Funzione per dati Free ---
def get_free_data():
    headers = {
        "x-apisports-key": API_FOOTBALL_KEY
    }
    response = requests.get(f"{API_FOOTBALL_URL}/fixtures?live=all", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get("response"):
            fixtures = data["response"]
            messages = []
            for f in fixtures[:5]:  # Primi 5 risultati
                home = f["fixture"]["home"]["name"]
                away = f["fixture"]["away"]["name"]
                score = f["score"]["fulltime"]
                messages.append(f"{home} vs {away} → {score['home']}:{score['away']}")
            return "\n".join(messages)
        return "Nessuna partita live al momento."
    else:
        return f"Errore API: {response.status_code}"

# --- Handlers Telegram ---
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    add_user(user_id, username)
    bot.send_message(user_id, "Benvenuto! Riceverai i pronostici ogni giorno!")

@bot.message_handler(commands=["list_users"])
def list_users_command(message):
    user_ids = get_all_users()
    bot.send_message(message.chat.id, f"Utenti registrati:\n{user_ids}")

@bot.message_handler(commands=["free"])
def free_command(message):
    try:
        data = get_free_data()
        bot.send_message(message.chat.id, data)
    except Exception as e:
        bot.send_message(message.chat.id, f"Errore nel recupero dati: {e}")

# --- Webhook Telegram ---
@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    try:
        json_str = request.get_data(as_text=True)
        logger.info("📩 Update ricevuto da Telegram: %s", json_str)
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
    except Exception as e:
        logger.error("Errore webhook Telegram: %s", e)
        return jsonify({"error": str(e)}), 400
    return jsonify({"status": "ok"}), 200

# --- Endpoint admin ---
@app.route("/admin/send_today", methods=["POST"])
def send_today():
    token = request.args.get("token")
    if token != ADMIN_TOKEN:
        return jsonify({"error": "Forbidden"}), 403
    try:
        for uid in get_all_users():
            send_daily_to_user(bot, uid)
    except Exception as e:
        logger.error("Errore invio pronostici: %s", e)
        return jsonify({"error": str(e)}), 500
    return jsonify({"status": "invio avviato"}), 200

# --- Webhook Stripe ---
@app.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    try:
        success = handle_stripe_webhook(payload, sig_header)
    except Exception as e:
        logger.error("Errore webhook Stripe: %s", e)
        return jsonify({"error": str(e)}), 400

    return jsonify({"status": "ok"}), 200 if success else 400

# --- Health check ---
@app.route("/healthz")
def health():
    return jsonify({"status": "ok"}), 200

# --- Test endpoint ---
@app.route("/test")
def test():
    return jsonify({"status": "server ok"}), 200

# --- Main ---
if __name__ == "__main__":
    init_db()
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/telegram")
    logger.info("Bot webhook impostato su %s/telegram", WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
