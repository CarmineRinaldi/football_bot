import os
import sqlite3
import stripe
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configurazioni da variabili di ambiente
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DATABASE_URL = os.getenv("DATABASE_URL", "users.db")

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET")
STRIPE_PRICE_2EUR = os.getenv("STRIPE_PRICE_2EUR")
STRIPE_PRICE_VIP = os.getenv("STRIPE_PRICE_VIP")

FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))

stripe.api_key = STRIPE_SECRET_KEY

# --- Database init ---
def init_db():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id TEXT UNIQUE,
            subscription TEXT DEFAULT 'free',
            matches_used INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Helpers ---
def get_user(tg_id):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE tg_id=?", (tg_id,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(tg_id):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (tg_id) VALUES (?)", (tg_id,))
    conn.commit()
    conn.close()

def update_subscription(tg_id, sub_type):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("UPDATE users SET subscription=?, matches_used=0 WHERE tg_id=?", (sub_type, tg_id))
    conn.commit()
    conn.close()

# --- Telegram Webhook ---
@app.route(f"/{TG_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        add_user(str(chat_id))

        if text == "/start":
            send_message(chat_id, "👋 Benvenuto! Sei in piano FREE.\nUsa /buy per abbonarti.")
        elif text == "/buy":
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                mode="subscription",
                line_items=[{"price": STRIPE_PRICE_2EUR, "quantity": 1}],
                success_url=WEBHOOK_URL + "/success",
                cancel_url=WEBHOOK_URL + "/cancel",
                metadata={"tg_id": str(chat_id)}
            )
            send_message(chat_id, f"💳 Abbonati qui: {session.url}")
        elif text == "/vip":
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                mode="subscription",
                line_items=[{"price": STRIPE_PRICE_VIP, "quantity": 1}],
                success_url=WEBHOOK_URL + "/success",
                cancel_url=WEBHOOK_URL + "/cancel",
                metadata={"tg_id": str(chat_id)}
            )
            send_message(chat_id, f"💎 VIP: {session.url}")
        else:
            send_message(chat_id, "❓ Comando non riconosciuto.")

    return jsonify({"status": "ok"})

# --- Stripe Webhook ---
@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_ENDPOINT_SECRET)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        tg_id = session["metadata"]["tg_id"]
        price_id = session["display_items"][0]["price"]["id"] if "display_items" in session else None

        if price_id == STRIPE_PRICE_2EUR:
            update_subscription(tg_id, "premium")
        elif price_id == STRIPE_PRICE_VIP:
            update_subscription(tg_id, "vip")

        send_message(tg_id, "✅ Pagamento ricevuto! Il tuo piano è stato attivato.")

    return jsonify({"status": "success"})

# --- Telegram Send Message ---
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

# --- Home route ---
@app.route("/")
def home():
    return "Bot attivo ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
