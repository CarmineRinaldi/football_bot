import stripe
from flask import request
from config import STRIPE_SECRET_KEY, STRIPE_ENDPOINT_SECRET

stripe.api_key = STRIPE_SECRET_KEY

def create_checkout_session(price_id, success_url, cancel_url):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        mode='payment',
        line_items=[{'price': price_id, 'quantity': 1}],
        success_url=success_url,
        cancel_url=cancel_url
    )
    return session.url

def verify_webhook(request):
    payload = request.data
    sig_header = request.headers.get('stripe-signature')
    event = None
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_ENDPOINT_SECRET)
    except Exception as e:
        print("Webhook error:", e)
    return event
