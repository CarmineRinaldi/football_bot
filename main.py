import os
from flask import Flask, request
from bot_logic import start, show_main_menu, show_leagues, show_matches, create_ticket
from stripe_webhook import handle_stripe_webhook

app = Flask(__name__)

TG_TOKEN = os.getenv("TG_BOT_TOKEN")

@app.route("/")
def home():
    return "Bot online"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    print("Webhook ricevuto:", update)

    if 'message' in update and 'text' in update['message']:
        text = update['message']['text']
        if text == "/start":
            resp = start(update, None)
        elif text in ["Free", "2€", "VIP"]:
            resp = show_main_menu(update, None)
        elif text == "Indietro":
            resp = show_main_menu(update, None)
        else:
            resp = {"text": "Comando non riconosciuto.", "keyboard": [["Indietro"]]}
        
        chat_id = update['message']['chat']['id']
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                      json={"chat_id": chat_id, "text": resp["text"]})
    return "OK", 200

@app.route("/stripe_webhook", methods=["POST"])
def stripe_hook():
    return handle_stripe_webhook()

if __name__ == "__main__":
    app.run(debug=True)
