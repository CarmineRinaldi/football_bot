import os
import sqlite3
import stripe
import requests
from flask import Flask, request, jsonify

# Flask app
app = Flask(__name__)

# Config da variabili d'ambiente
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "users.db")

FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET")
STRIPE_PRICE_2EUR = os.getenv("STRIPE_PRICE_2EUR")
STRIPE_PRICE_VIP = os.getenv("STRIPE_PRICE_VIP")

stripe.api_key = STRIPE_SECRET_KEY


# ========= Database =========
def init_db():
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT UNIQUE,
            subscription TEXT DEFAULT 'free'
        )
    """)
    conn.commit()
    conn.close()


init_db()


# ========= Telegram =========
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)


@app.route(f"/{TG_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json()

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "Benvenuto! 🎉 Puoi cercare le partite con /matches.")
        elif text == "/matches":
            conn = sqlite3.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute("SELECT subscription FROM users WHERE chat_id = ?", (chat_id,))
            row = cursor.fetchone()

            max_matches = FREE_MAX_MATCHES
            if row and row[0] == "vip":
                max_matches = VIP_MAX_MATCHES

            # Chiamata API Football
            headers = {"x-apisports-key": API_FOOTBALL_KEY}
            r = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=headers)
            data = r.json()

            matches = data.get("response", [])[:max_matches]
            if not matches:
                send_message(chat_id, "⚽ Nessuna partita trovata.")
            else:
                for match in matches:
                    teams = f"{match['teams']['home']['name']} vs {match['teams']['away']['name']}"
                    score = f"{match['goals']['home']} - {match['goals']['away']}"
                    send_message(chat_id, f"{teams}\nRisultato: {score}")

            conn.close()

    return jsonify({"ok": True})


# ========= Stripe Webhook =========
@app.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_ENDPOINT_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return "Signature verification failed", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        chat_id = session["client_reference_id"]

        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (chat_id, subscription) VALUES (?, 'vip')", (chat_id,))
        cursor.execute("UPDATE users SET subscription = 'vip' WHERE chat_id = ?", (chat_id,))
        conn.commit()
        conn.close()

        send_message(chat_id, "✅ Complimenti! Sei passato a VIP. Puoi vedere più partite.")

    return "ok", 200


# ========= Root =========
@app.route("/")
def home():
    return "⚽ Football Bot attivo su Render!"


# ========= Run locale =========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
