# main.py
import os
import sqlite3
import json
import requests
import stripe
from flask import Flask, request, jsonify

# -------------------------
# Config (leggi da env)
# -------------------------
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # es: https://your-app.onrender.com
DATABASE_URL = os.getenv("DATABASE_URL", "users.db")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")

FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET")
STRIPE_PRICE_2EUR = os.getenv("STRIPE_PRICE_2EUR")
STRIPE_PRICE_VIP = os.getenv("STRIPE_PRICE_VIP")

# Basic checks (fail fast with clear message)
required = {
    "TG_BOT_TOKEN": TG_BOT_TOKEN,
    "WEBHOOK_URL": WEBHOOK_URL,
    "STRIPE_SECRET_KEY": STRIPE_SECRET_KEY,
    "STRIPE_ENDPOINT_SECRET": STRIPE_ENDPOINT_SECRET,
}
missing = [k for k, v in required.items() if not v]
if missing:
    # don't crash silently on render logs — raise so you see it clearly
    raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")

stripe.api_key = STRIPE_SECRET_KEY

# -------------------------
# App & DB init
# -------------------------
app = Flask(__name__)

def init_db():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            tg_id TEXT PRIMARY KEY,
            username TEXT,
            subscription TEXT DEFAULT 'free',
            matches_used INTEGER DEFAULT 0,
            stored_tickets TEXT DEFAULT '[]'
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -------------------------
# Helpers
# -------------------------
TELEGRAM_API = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"

def send_message(chat_id, text, parse_mode=None):
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", json=payload, timeout=10)
    except Exception as e:
        # log to stdout/stderr so Render shows it
        print("send_message error:", e)

def get_user(tg_id):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("SELECT tg_id, username, subscription, matches_used, stored_tickets FROM users WHERE tg_id = ?", (tg_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    tg_id, username, subscription, matches_used, stored_tickets = row
    try:
        tickets = json.loads(stored_tickets)
    except Exception:
        tickets = []
    return {"tg_id": tg_id, "username": username, "subscription": subscription, "matches_used": matches_used, "tickets": tickets}

def ensure_user(tg_id, username=None):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (tg_id, username) VALUES (?, ?)", (tg_id, username))
    # update username if changed
    if username:
        c.execute("UPDATE users SET username = ? WHERE tg_id = ?", (username, tg_id))
    conn.commit()
    conn.close()

def set_subscription(tg_id, plan):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("UPDATE users SET subscription = ?, matches_used = 0 WHERE tg_id = ?", (plan, tg_id))
    conn.commit()
    conn.close()

def increment_matches_used(tg_id):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("UPDATE users SET matches_used = matches_used + 1 WHERE tg_id = ?", (tg_id,))
    conn.commit()
    conn.close()

def save_ticket(tg_id, ticket):
    user = get_user(tg_id)
    tickets = user["tickets"] if user else []
    tickets.append(ticket)
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("UPDATE users SET stored_tickets = ? WHERE tg_id = ?", (json.dumps(tickets), tg_id))
    conn.commit()
    conn.close()

# -------------------------
# Telegram webhook endpoint
# route uses token path for security: /<TG_BOT_TOKEN>
# -------------------------
@app.route(f"/{TG_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json(force=True)

    # handle messages only (extend as needed)
    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return jsonify({"ok": True})

    chat = msg.get("chat", {})
    chat_id = str(chat.get("id"))
    username = msg.get("from", {}).get("username")
    text = msg.get("text", "").strip()

    ensure_user(chat_id, username)

    # Commands
    if text.startswith("/start"):
        send_message(chat_id, "👋 Benvenuto! Usa /matches per vedere pronostici, /buy per offerte, /myschedine per le tue schedine.")
        return jsonify({"ok": True})

    if text.startswith("/matches"):
        user = get_user(chat_id)
        sub = user["subscription"] if user else "free"
        limit = VIP_MAX_MATCHES if sub == "vip" else FREE_MAX_MATCHES

        # SAMPLE: call API-Football for upcoming fixtures (example)
        headers = {"x-apisports-key": API_FOOTBALL_KEY}
        try:
            r = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=headers, timeout=10)
            data = r.json()
            fixtures = data.get("response", [])[:limit]
        except Exception as e:
            print("API-Football error:", e)
            fixtures = []

        if not fixtures:
            send_message(chat_id, "Nessuna partita disponibile ora.")
        else:
            for f in fixtures:
                home = f["teams"]["home"]["name"]
                away = f["teams"]["away"]["name"]
                time = f.get("fixture", {}).get("date", "—")
                send_message(chat_id, f"{home} vs {away}\nOrario: {time}")
        return jsonify({"ok": True})

    if text.startswith("/myschedine"):
        user = get_user(chat_id)
        tickets = user["tickets"] if user else []
        if not tickets:
            send_message(chat_id, "Non hai schedine salvate.")
        else:
            for i, t in enumerate(tickets, 1):
                send_message(chat_id, f"Schedina {i}: {json.dumps(t)}")
        return jsonify({"ok": True})

    if text.startswith("/buy") or text.startswith("/vip"):
        # open stripe checkout session (client_reference_id = chat_id)
        price = STRIPE_PRICE_2EUR if text.startswith("/buy") else STRIPE_PRICE_VIP
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{"price": price, "quantity": 1}],
                mode="payment",
                success_url=WEBHOOK_URL + "/success?tg_id=" + chat_id,
                cancel_url=WEBHOOK_URL + "/cancel?tg_id=" + chat_id,
                client_reference_id=chat_id
            )
            send_message(chat_id, f"Apri il pagamento: {session.url}")
        except Exception as e:
            print("Stripe session error:", e)
            send_message(chat_id, "Errore durante la creazione del pagamento.")
        return jsonify({"ok": True})

    # default response
    send_message(chat_id, "Comando non riconosciuto. Usa /start.")
    return jsonify({"ok": True})

# -------------------------
# Stripe webhook (server-to-server)
# -------------------------
@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")
    try:
        ev = stripe.Webhook.construct_event(payload, sig_header, STRIPE_ENDPOINT_SECRET)
    except Exception as e:
        print("Stripe webhook error:", e)
        return "Invalid signature", 400

    # handle checkout session completed
    if ev["type"] == "checkout.session.completed":
        session = ev["data"]["object"]
        tg_id = session.get("client_reference_id") or session.get("metadata", {}).get("tg_id")
        # If you use price IDs to distinguish:
        # price_id = session["display_items"][0]["price"]["id"]  # older payloads
        # Decide plan by session.content or client_reference
        # For simplicity, mark any completed session as premium (or examine session['amount_total'])
        if tg_id:
            set_subscription(tg_id, "vip")
            send_message(tg_id, "✅ Pagamento ricevuto — sei VIP ora.")
    return jsonify({"ok": True})

# -------------------------
# Health & success routes
# -------------------------
@app.route("/")
def index():
    return "Football Bot attivo"

@app.route("/success")
def success_page():
    tg_id = request.args.get("tg_id")
    return f"Pagamento completato. Torna su Telegram (chat: {tg_id})."

@app.route("/cancel")
def cancel_page():
    return "Pagamento annullato."

# -------------------------
# Utility: set webhook manually (not auto-run)
# -------------------------
def set_telegram_webhook():
    # Call this manually once (locally or via a one-time script) AFTER deploy
    webhook_url = f"{WEBHOOK_URL}/{TG_BOT_TOKEN}"
    r = requests.get(f"{TELEGRAM_API}/setWebhook?url={webhook_url}")
    print("setWebhook response:", r.text)
    return r.ok

# -------------------------
# Run (for local testing)
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
