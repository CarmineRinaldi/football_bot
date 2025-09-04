import os
from flask import Flask, request
from queue_handler import UpdateQueue
from bot_commands import handle_update

app = Flask(__name__)
update_queue = UpdateQueue()

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    if update:
        update_queue.put(update)
        return "OK", 200
    return "No update", 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
