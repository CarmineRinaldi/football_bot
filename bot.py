from flask import Flask, request, jsonify
import os
import telebot
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import init_db, add_user, get_all_users, get_user, set_vip, set_plan
from bot_logic import send_daily_to_user
from payments import handle_stripe_webhook

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram / Webhook
TOKEN = os.environ.get("TG_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
ADMIN_TOKEN = os.environ.get("ADMIN_HTTP_TOKEN", "metti_un_token_lungo")

if not TOKEN or not WEBHOOK_URL:
    logger.error("Variabili TG_BOT_TOKEN o WEBHOOK_URL mancanti!")
    exit(1)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# =========================
# Menu inline
# =========================
def main_menu(user_id):
    markup = InlineKeyboardMarkup()
    markup.row
