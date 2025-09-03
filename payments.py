import stripe
import os
from db import set_user_plan, increment_user_tickets  # assume increment_user_tickets è implementata

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# =========================
# Price IDs Stripe
# =========================
STRIPE_PRICE_VIP = "prod_SzHNxZCTAwhDN8"   # Abbonamento mensile VIP
STRIPE_PRICE_PACK = "prod_SzHRKztJPEsrLS"  # Pacchetto 2€ di pronostici

# =========================
# Crea sessione Checkout Stripe
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
            payload, sig_header, os.environ.get("STRIPE_ENDPOINT_SECRET")
        )
    except Exception as e:
        raise e

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        product_type = session['metadata']['product_type']

        # Aggiorna DB utente
        if product_type == "vip":
            set_user_plan(user_id, "vip")
        elif product_type == "pack":
            # aggiunge 10 schedine extra
            increment_user_tickets(user_id, 10)

    return True
