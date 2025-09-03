import os
import logging
from flask import Flask, request, jsonify
import telebot
from datetime import date

# --- moduli locali ---
from db import init_db, add_user, get_all_users, is_vip_user, get_user_tickets
from bot_logic import send_daily_to_user, generate_daily_tickets_for_user

# =========================
# Config & oggetti globali
# =========================
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TG_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
ADMIN_TOKEN = os.environ.get("ADMIN_HTTP_TOKEN", "changeme-super-long")
TG_SECRET = os.environ.get("TG_WEBHOOK_SECRET")

if not TOKEN or not WEBHOOK_URL:
    logger.error("🚨 TG_BOT_TOKEN o WEBHOOK_URL mancanti!")
    raise RuntimeError("Variabili obbligatorie mancanti")

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# =========================
# Inizializza DB
# =========================
try:
    init_db()
    logger.info("DB inizializzato correttamente.")
except Exception as e:
    logger.exception("Errore inizializzazione DB: %s", e)

# =========================
# Health & index
# =========================
@app.get("/")
def index():
    return jsonify({"service": "football-bot", "status": "ok"}), 200

@app.get("/healthz")
def health():
    return jsonify({"status": "ok"}), 200

# =========================
# Webhook Telegram
# =========================
@app.route("/telegram", methods=["POST", "GET"])
def telegram_webhook():
    if request.method == "GET":
        return jsonify({"status": "ok"}), 200
    if TG_SECRET:
        secret_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret_header != TG_SECRET:
            logger.warning("Tentativo webhook con secret errato.")
            return jsonify({"error": "forbidden"}), 403
    try:
        json_str = request.get_data(as_text=True)
        logger.info("📩 Update ricevuto da Telegram: %s", json_str)
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.exception("Errore nel processamento dell'update Telegram: %s", e)
        return jsonify({"error": str(e)}), 400

# =========================
# Handlers Telegram
# =========================
@bot.message_handler(commands=["start"])
def start(message):
    try:
        user_id = message.from_user.id
        username = (message.from_user.username or "").strip()
        add_user(user_id, username)

        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row("/mytickets", "/upgrade")
        keyboard.row("Aiuto")

        bot.send_message(
            user_id,
            "Benvenuto! Usa i pulsanti qui sotto per navigare tra i comandi:",
            reply_markup=keyboard
        )
        logger.info("Registrato utente %s (@%s)", user_id, username)
    except Exception as e:
        logger.exception("Errore handler /start: %s", e)

@bot.message_handler(commands=["mytickets"])
def mytickets(message):
    try:
        user_id = message.from_user.id
        vip = is_vip_user(user_id)
        today = str(date.today())

        # Genera schedine se non ci sono
        generate_daily_tickets_for_user(user_id, vip)
        tickets = get_user_tickets(user_id, today)

        if not tickets:
            bot.send_message(user_id, "Non ci sono schedine disponibili oggi.")
            return

        for idx, t in enumerate(tickets, 1):
            # Estrazione sicura dei pronostici
            preds = []
            if isinstance(t, dict):
                if "predictions" in t and isinstance(t["predictions"], list):
                    preds = t["predictions"]
                elif "data" in t and isinstance(t["data"], dict):
                    preds = t["data"].get("predictions", [])
            if not isinstance(preds, list):
                preds = []

            if not preds:
                continue

            if not vip:
                preds = preds[:3]  # Free → solo 3 pronostici

            msg = f"🎟️ Schedina {idx}:\n" + "\n".join(preds)
            bot.send_message(user_id, msg)

    except Exception as e:
        logger.exception("Errore handler /mytickets: %s", e)
        bot.send_message(message.chat.id, "Errore nel recupero schedine.")

@bot.message_handler(commands=["upgrade"])
def upgrade(message):
    try:
        user_id = message.from_user.id
        bot.send_message(
            user_id,
            "🔥 Vuoi diventare VIP e sbloccare tutte le schedine e pronostici?\n"
            "Visita questo link per il pagamento e upgrade: [INSERISCI LINK STRIPE QUI]"
        )
    except Exception as e:
        logger.exception("Errore handler /upgrade: %s", e)
        bot.send_message(message.chat.id, "Errore nel processo di upgrade.")

@bot.message_handler(func=lambda m: True)
def echo(message):
    try:
        logger.info("Msg da %s: %s", message.chat.id, message.text)
        bot.send_message(message.chat.id, f"Hai scritto: {message.text}")
    except Exception as e:
        logger.exception("Errore echo: %s", e)

# =========================
# Admin endpoints
# =========================
def _is_admin(req) -> bool:
    return req.args.get("token") == ADMIN_TOKEN

@app.post("/admin/send_today")
def send_today():
    if not _is_admin(request):
        return jsonify({"error": "Forbidden"}), 403
    try:
        for uid in get_all_users():
            send_daily_to_user(bot, uid)
        return jsonify({"status": "invio avviato"}), 200
    except Exception as e:
        logger.exception("Errore invio pronostici: %s", e)
        return jsonify({"error": "internal"}), 500
