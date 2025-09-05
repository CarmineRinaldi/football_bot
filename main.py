import os
from flask import Flask, request
from bot_logic import handle_update

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Bot is live", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    print("Webhook ricevuto:", update)
    handle_update(update)
    return {"status": "ok"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
