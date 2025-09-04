import os
import logging
import sqlite3
import threading
from flask import Flask, request, jsonify
import requests

from football_api import get_leagues, get_matches  # import corretto
from config import TELEGRAM_TOKEN

# -------------------------------
# Logging
# -------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------
# Flask app
# -------------------------------
app = Flask(__name__)

# -------------------------------
# Database SQLite thread-safe
# -------------------------------
DB_FILE = 'users.db'
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()
db_lock = threading.Lock()

with db_lock:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT UNIQUE,
            username TEXT
        )
    ''')
    conn.commit()

# -------------------------------
# Route di test
# -------------------------------
@app.route('/')
def index():
    return "Bot football attivo ✅"

# -------------------------------
# Webhook Telegram
# -------------------------------
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "no data"}), 400

        logger.info(f"Ricevuto webhook: {data}")

        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')

        # Salva utente
        with db_lock:
            cursor.execute("INSERT OR IGNORE INTO users (chat_id) VALUES (?)", (chat_id,))
            conn.commit()

        # Risposta comandi
        if text.lower() == '/start':
            send_message(chat_id, "Ciao! Bot attivo. Usa /leagues o /matches.")
        elif text.lower() == '/leagues':
            leagues_info = get_leagues()
            leagues_text = "\n".join([league.get('name', 'N/A') for league in leagues_info.get('response', [])[:10]])
            send_message(chat_id, f"Top 10 leghe:\n{leagues_text}")
        elif text.lower() == '/matches':
            matches_info = get_matches()
            matches_text = "\n".join([f"{m['fixture']['home']['name']} vs {m['fixture']['away']['name']}" 
                                      for m in matches_info.get('response', [])[:10]])
            send_message(chat_id, f"Top 10 partite:\n{matches_text}")
        else:
            send_message(chat_id, "Comando non riconosciuto.")

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        logger.error(f"Errore webhook: {e}")
        return jsonify({"status": "error"}), 500

# -------------------------------
# Funzione invio messaggi Telegram
# -------------------------------
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        r = requests.post(url, json=payload)
        if r.status_code != 200:
            logger.warning(f"Errore invio messaggio: {r.text}")
    except Exception as e:
        logger.error(f"Errore richieste Telegram: {e}")

# -------------------------------
# Avvio app
# -------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
