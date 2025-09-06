import os
import stripe
from db import add_user

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET")

def handle_stripe_event(payload, sig_header):
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, ENDPOINT_SECRET)
    except stripe.error.SignatureVerificationError:
        return {"status": 400}

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = int(session["client_reference_id"])
        price_id = session["display_items"][0]["price"]["id"]
        plan = "2eur" if price_id == os.getenv("STRIPE_PRICE_2EUR") else "vip"
        add_user(user_id, plan)
    return {"status": 200}
