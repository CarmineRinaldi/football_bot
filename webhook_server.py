import os
import sqlite3
import threading
from queue import Queue
from flask import Flask, request, jsonify
import stripe

# -------------------------------
# Config
# -------------------------------
DB_FILE = os.environ.get("DB_FILE", "users.db")
ADMIN_HTTP_TOKEN = os.environ.get("ADMIN_HTTP_TOKEN")
API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY")
FREE_MAX_MATCHES = int(os.environ.get("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.environ.get("VIP_MAX_MATCHES", 20))
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET = os.environ.get("STRIPE_ENDPOINT_SECRET")
STRIPE_PRICE_2EUR = os.environ.get("STRIPE_PRICE_2EUR")
STRIPE_PRICE_VIP = os.environ.get("STRIPE_PRICE_VIP")
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

stripe.api_key = STRIPE_SECRET_KEY

# -------------------------------
# DB Connection
# -------------------------------
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()
db_lock = threading.Lock()

# -------------------------------
# Flask App
# -------------------------------
app = Flask(__name__)
update_queue = Queue()

# -------------------------------
# Routes
# -------------------------------
@app.route("/")
def home():
    return "Bot is running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return "No data", 400

    update_queue.put(data)
    return "OK", 200

@app.route("/admin", methods=["POST"])
def admin():
    token = request.headers.get("Authorization")
    if token != f"Bearer {ADMIN_HTTP_TOKEN}":
        return "Unauthorized", 401

    return jsonify({"status": "ok"}), 200

# -------------------------------
# Stripe webhook
# -------------------------------
@app.route("/stripe_webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_ENDPOINT_SECRET
        )
    except ValueError:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    # Esempio: gestione pagamenti
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        handle_payment(session)

    return "OK", 200

def handle_payment(session):
    customer_email = session.get("customer_email")
    price_id = session.get("line_items", [{}])[0].get("price", "")
    print(f"Payment received: {customer_email}, price: {price_id}")
    # Aggiorna DB o invia messaggio Telegram

# -------------------------------
# Queue processing
# -------------------------------
def process_updates():
    while True:
        update = update_queue.get()
        try:
            handle_update(update)
        finally:
            update_queue.task_done()

def handle_update(update):
    print("Received update:", update)
    # Inserisci qui la logica per API Football o Telegram

threading.Thread(target=process_updates, daemon=True).start()

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
