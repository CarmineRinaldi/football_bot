import os
import stripe
from flask import request

STRIPE_SECRET_KEY = os.environ["STRIPE_SECRET_KEY"]
STRIPE_ENDPOINT_SECRET = os.environ["STRIPE_ENDPOINT_SECRET"]
stripe.api_key = STRIPE_SECRET_KEY

def handle_stripe_event(req):
    payload = req.data
    sig_header = req.headers.get("Stripe-Signature")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_ENDPOINT_SECRET
        )
    except Exception as e:
        return str(e), 400

    # gestione eventi pagamento completato
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        chat_id = session["client_reference_id"]
        # aggiorna piano utente su DB
        from db import get_user, create_user
        user = get_user(chat_id)
        if user:
            # aggiorna piano in DB
            pass

    return "", 200
