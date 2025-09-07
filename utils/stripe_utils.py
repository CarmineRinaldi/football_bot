import os
import stripe

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
PRICE_2EUR = os.environ.get("STRIPE_PRICE_2EUR")
PRICE_VIP = os.environ.get("STRIPE_PRICE_VIP")

def create_checkout_session(user_id, price_id, success_url, cancel_url):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription" if price_id == PRICE_VIP else "payment",
        metadata={"user_id": user_id},
        success_url=success_url,
        cancel_url=cancel_url
    )
    return session.url
