import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Home
@app.route("/")
def home():
    return "Server Online"

# Webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("Webhook ricevuto:", data)
        # Qui puoi aggiungere la logica per processare i dati
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print("Errore webhook:", e)
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
