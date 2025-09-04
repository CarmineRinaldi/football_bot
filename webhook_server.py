import os
import sqlite3
import threading
from queue import Queue
from flask import Flask, request, jsonify

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

# -------------------------------
# Thread-safe queue
# -------------------------------
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

    # Inserisco nella queue in modo thread-safe
    update_queue.put(data)
    return "OK", 200

@app.route("/admin", methods=["POST"])
def admin():
    token = request.headers.get("Authorization")
    if token != f"Bearer {ADMIN_HTTP_TOKEN}":
        return "Unauthorized", 401

    return jsonify({"status": "ok"}), 200

# -------------------------------
# Helper per gestire queue
# -------------------------------
def process_updates():
    while True:
        update = update_queue.get()
        try:
            handle_update(update)
        finally:
            update_queue.task_done()

def handle_update(update):
    # Qui va la logica di gestione degli update
    print("Received update:", update)
    # Esempio: puoi integrare chiamate API Football o Telegram

# -------------------------------
# Thread per processare gli update
# -------------------------------
threading.Thread(target=process_updates, daemon=True).start()

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
