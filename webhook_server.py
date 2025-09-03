# webhook_server.py
import os
import logging
from flask import Flask, request, jsonify
import telebot

# --- moduli locali ---
from db import init_db, add_user, get_all_users
from bot_logic import send_daily_to_user

# =========================
# Config & oggetti globali
# =========================
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TG_BOT_TOKEN")                    # obbligatorio
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")               # es: https://football-bot-ric2.onrender.com
ADMIN_TOKEN = os.environ.get("ADMIN_HTTP_TOKEN", "changeme-super-long")
TG_SECRET = os.environ.get("TG_WEBHOOK_SECRET")           # opzionale: secret per sicurezza webhook

if not TOKEN or not WEBHOOK_URL:
    logger.error("🚨 TG_BOT_TOKEN o WEBHOOK_URL mancanti!")
    raise RuntimeError("Variabili obbligatorie mancanti")

# threaded=False evita problemi con Gunicorn
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

    # Controllo secret opzionale
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
        bot.send_message(user_id, "Benvenuto! Riceverai i pronostici ogni giorno!")
        logger.info("Registrato utente %s (@%s)", user_id, username)
    except Exception as e:
        logger.exception("Errore handler /start: %s", e)

@bot.message_handler(commands=["list_users"])
def list_users_command(message):
    try:
        ids = get_all_users()
        txt = "Utenti registrati:\n" + ("\n".join(map(str, ids)) if ids else "Nessun utente.")
        bot.send_message(message.chat.id, txt)
    except Exception as e:
        logger.exception("Errore handler /list_users: %s", e)

# Fallback: risponde a QUALSIASI messaggio
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

@app.post("/admin/set_webhook")
def admin_set_webhook():
    if not _is_admin(request):
        return jsonify({"error": "Forbidden"}), 403
    try:
        url = f"{WEBHOOK_URL.rstrip('/')}/telegram"
        bot.remove_webhook()
        bot.set_webhook(url=url, secret_token=TG_SECRET if TG_SECRET else None)
        info = bot.get_webhook_info()
        return jsonify({"status": "ok", "webhook": info.to_dict()}), 200
    except Exception as e:
        logger.exception("Errore set_webhook: %s", e)
        return jsonify({"error": "internal"}), 500

@app.post("/admin/delete_webhook")
def admin_delete_webhook():
    if not _is_admin(request):
        return jsonify({"error": "Forbidden"}), 403
    try:
        bot.delete_webhook(drop_pending_updates=False)
        info = bot.get_webhook_info()
        return jsonify({"status": "ok", "webhook": info.to_dict()}), 200
    except Exception as e:
        logger.exception("Errore delete_webhook: %s", e)
        return jsonify({"error": "internal"}), 500

# =========================
# Stripe webhook (lazy import)
# =========================
@app.post("/stripe/webhook")
def stripe_webhook():
    try:
        from payments import handle_stripe_webhook
    except Exception as e:
        logger.warning("Stripe non configurato o import fallito: %s", e)
        return jsonify({"error": "payments_not_configured"}), 501

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    try:
        ok = handle_stripe_webhook(payload, sig_header)
        return (jsonify({"status": "ok"}), 200) if ok else (jsonify({"error": "invalid"}), 400)
    except Exception as e:
        logger.exception("Errore webhook Stripe: %s", e)
        return jsonify({"error": "internal"}), 500

# =========================
# Fine file - pronto per Gunicorn/Render
# =========================
# Nota: NON serve app.run() su Render con Gunicorn
