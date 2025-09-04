import os
import stripe

STRIPE_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PRICE_2EUR = os.environ.get("STRIPE_PRICE_2EUR")
STRIPE_PRICE_VIP = os.environ.get("STRIPE_PRICE_VIP")
WEBHOOK_SECRET = os.environ.get("STRIPE_ENDPOINT_SECRET")

stripe.api_key = STRIPE_KEY

class StripeHandler:
    def create_payment_url(self, chat_id):
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": STRIPE_PRICE_VIP, "quantity": 1}],
            mode="payment",
            success_url=f"https://success.com?chat_id={chat_id}",
            cancel_url=f"https://cancel.com?chat_id={chat_id}",
        )
        return session.url
