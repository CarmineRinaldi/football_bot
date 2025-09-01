# webhook_server.py
from flask import Flask, request
import os
import telebot
from db import init_db, add_user, get_all_users
from bot_logic import send_daily_to_user

TOKEN = os.environ["TG_BOT_TOKEN"]
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- Handlers Telegram ---
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
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
ADMIN_TOKEN = os.environ.get("ADMIN_HTTP_TOKEN", "metti_un_token_lungo")

@app.route("/admin/send_today", methods=["POST"])
def send_today():
    token = request.args.get("token")
    if token != ADMIN_TOKEN:
        return "Forbidden", 403
    for uid in get_all_users():
        send_daily_to_user(bot, uid)
    return "Invio avviato", 200

if __name__ == "__main__":
    init_db()
    bot.remove_webhook()
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # es: https://tuoapp.onrender.com
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
