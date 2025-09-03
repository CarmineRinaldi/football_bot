import stripe
import os
from flask import request, jsonify

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# =========================
# Price IDs Stripe
# =========================
STRIPE_PRICE_VIP = "prod_SzHNxZCTAwhDN8"   # Abbonamento mensile VIP
STRIPE_PRICE_PACK = "prod_SzHRKztJPEsrLS"  # Pacchetto 2€ di pronostici

# =========================
# Funzione per creare Checkout session
# =========================
def create_checkout_session(user_id, product_type):
    if product_type == "vip":
        price_id = STRIPE_PRICE_VIP
    elif product_type == "pack":
        price_id = STRIPE_PRICE_PACK
    else:
        raise ValueError("Tipo prodotto sconosciuto")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="payment" if product_type == "pack" else "subscription",
        success_url=f"https://tuosito.com/success?user={user_id}&product={product_type}",
        cancel_url=f"https://tuosito.com/cancel",
        metadata={"user_id": user_id, "product_type": product_type}
    )
    return session.url

# =========================
# Gestione webhook Stripe
# =========================
def handle_stripe_webhook(payload, sig_header):
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get("STRIPE_WEBHOOK_SECRET")
        )
    except Exception as e:
        raise e

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        product_type = session['metadata']['product_type']
        # Qui aggiorni il piano o i pronostici dell’utente
        if product_type == "vip":
            from db import set_user_plan
            set_user_plan(user_id, "vip")
        elif product_type == "pack":
            from db import increment_user_tickets
            increment_user_tickets(user_id, 10)  # 10 pronostici da aggiungere

    return True
