import os
import stripe
from flask import Flask, request
from db import get_user, update_user_plan

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
endpoint_secret = os.environ.get("STRIPE_ENDPOINT_SECRET")
app = Flask(__name__)

@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        return str(e), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = int(session["client_reference_id"])
        user = get_user(user_id) or {"plan":"free", "credits":0}
        amount = session["amount_total"]
        if amount == 200:
            user["plan"] = "paid"
            user["credits"] = user.get("credits",0) + 10
        elif amount == 499:
            user["plan"] = "vip"
            user["vip_until"] = int(time.time()) + 30*24*60*60
        update_user_plan(user_id, user["plan"], user.get("credits",0), user.get("vip_until",0))

    return "", 200
