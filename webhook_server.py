from flask import Flask, request, jsonify
import os
import telebot
import logging
from db import init_db, add_user, get_all_users
from bot_logic import send_daily_to_user
from payments import handle_stripe_webhook

# --- Config logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Variabili d'ambiente ---
TOKEN = "8488759682:AAEdaxTctJ1Yy21fIhXqIl9Y3IJf2VdJnC8"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # es: https://football-bot-ric2.onrender.com
ADMIN_TOKEN = os.environ.get("ADMIN_HTTP_TOKEN", "metti_un_token_lungo")

if not WEBHOOK_URL:
    logger.error("Variabile WEBHOOK_URL mancante!")
    exit(1)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- Handlers Telegram ---
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    add_user(user_id, username)
    bot.send_message(user_id, "Benvenuto! Riceverai i pronostici ogni giorno!")

# --- Webhook Telegram ---
@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    try:
        json_str = request.get_data(as_text=True)
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
    except Exception as e:
        logger.error("Errore webhook Telegram: %s", e)
        return jsonify({"error": str(e)}), 400
    return jsonify({"status": "ok"}), 200

# --- Endpoint admin per invio pronostici ---
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

    if success:
        return jsonify({"status": "ok"}), 200
    else:
        return jsonify({"error": "Stripe webhook failed"}), 400

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
@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    try:
        json_str = request.get_data(as_text=True)
        logger.info("📩 Update ricevuto da Telegram: %s", json_str)  # 👈 DEBUG
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
    except Exception as e:
        logger.error("Errore webhook Telegram: %s", e)
        return jsonify({"error": str(e)}), 400
    return jsonify({"status": "ok"}), 200
