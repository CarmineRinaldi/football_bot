# send_daily_script.py
import os
import logging
import sys
from bot_logic import send_daily_to_user
from db import get_all_users
import telebot

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# --- Telegram Bot ---
TOKEN = os.environ.get("TG_BOT_TOKEN")
if not TOKEN:
    logger.error("Variabile TG_BOT_TOKEN mancante!")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# --- DB mode (SQLite o Postgres) ---
DB_FILE = os.environ.get("DB_FILE", "users.db")
DATABASE_URL = os.environ.get("DATABASE_URL")  # opzionale se PostgreSQL

logger.info("Avvio invio pronostici...")
logger.info("DB_FILE=%s | DATABASE_URL=%s", DB_FILE, DATABASE_URL)

def main():
    try:
        users = get_all_users()
    except Exception as e:
        logger.error("Errore lettura utenti dal DB: %s", e)
        return

    if not users:
        logger.info("Nessun utente trovato nel DB.")
        return

    logger.info("Invio pronostici a %d utenti...", len(users))

    for user_id in users:
        try:
            send_daily_to_user(bot, user_id)
            logger.info("Pronostici inviati a user_id=%s", user_id)
        except Exception as e:
            logger.error("Errore invio a user_id=%s: %s", user_id, e)

    logger.info("Invio completato!")

if __name__ == "__main__":
    main()
