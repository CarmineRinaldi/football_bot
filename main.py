import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Token Telegram in environment
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# Comandi supportati
def handle_start(chat_id):
    send_message(chat_id, "Ciao! Bot attivo e pronto a funzionare.")

def handle_help(chat_id):
    send_message(chat_id, "Lista comandi disponibili:\n/start - Avvia il bot\n/help - Mostra questa guida")

# Funzione per inviare messaggi
def send_message(chat_id, text):
    payload = {"chat_id": chat_id, "text": text}
    r = requests.post(BASE_URL, json=payload)
    return r.json()

# Route principale
@app.route("/")
def home():
    return "Server Online"

# Webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("Webhook ricevuto:", data)

        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")

            # Logica dei comandi
            if text == "/start":
                handle_start(chat_id)
            elif text == "/help":
                handle_help(chat_id)
            else:
                send_message(chat_id, f"Hai scritto: {text}")

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Errore webhook:", e)
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
