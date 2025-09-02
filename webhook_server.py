from flask import Flask, request
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
TOKEN = os.environ.get("TG_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # es: https://tuoapp.onrender.com
ADMIN_TOKEN = os.environ.get("ADMIN_HTTP_TOKEN", "metti_un_token_lungo")

if not TOKEN or not WEBHOOK_URL:
    logger.error("Variabili TG_BOT_TOKEN o WEBHOOK_URL mancanti!")
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
@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# --- Endpoint admin per invio pronostici ---
@app.route("/admin/send_today", methods=["POST"])
def send_today():
    token = request.args.get("token")
    if token != ADMIN_TOKEN:
        return "Forbidden", 403
    for uid in get_all_users():
        send_daily_to_user(bot, uid)
    return "Invio avviato", 200

# --- Webhook Stripe ---
@app.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    success = handle_stripe_webhook(payload, sig_header)
    return ("OK", 200) if success else ("Errore", 400)

# --- Health check ---
@app.route("/healthz")
def health():
    return {"status": "ok"}, 200

# --- Main ---
if __name__ == "__main__":
    init_db()
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    logger.info("Bot webhook impostato su %s/%s", WEBHOOK_URL, TOKEN)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
