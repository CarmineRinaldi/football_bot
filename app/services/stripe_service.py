import stripe
from fastapi import HTTPException
from app.utils.config import settings
from app.utils.logger import logger


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_oneoff(success_url: str, cancel_url: str, price_id: str, metadata: dict = None):
try:
session = stripe.checkout.Session.create(
payment_method_types=["card"],
mode="payment",
line_items=[{"price": price_id, "quantity": 1}],
success_url=success_url,
cancel_url=cancel_url,
metadata=metadata or {},
)
return session
except Exception as e:
logger.exception("stripe checkout create failed")
raise HTTPException(status_code=500, detail=str(e))


def create_checkout_subscription(success_url: str, cancel_url: str, price_id: str, metadata: dict = None):
try:
session = stripe.checkout.Session.create(
payment_method_types=["card"],
mode="subscription",
line_items=[{"price": price_id, "quantity": 1}],
success_url=success_url,
cancel_url=cancel_url,
metadata=metadata or {},
)
return session
except Exception as e:
logger.exception("stripe subscription create failed")
raise HTTPException(status_code=500, detail=str(e))


def construct_event(payload: bytes, sig_header: str):
try:
event = stripe.Webhook.construct_event(
payload, sig_header, settings.STRIPE_ENDPOINT_SECRET
)
return event
except stripe.error.SignatureVerificationError as e:
logger.exception("Stripe webhook signature verification failed")
raise HTTPException(status_code=400, detail="Invalid signature")
