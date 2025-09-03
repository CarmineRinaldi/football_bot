import stripe
from config import STRIPE_SECRET_KEY

stripe.api_key = STRIPE_SECRET_KEY

def create_checkout_session(user_id, price_id):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='payment',
        success_url=f"https://tuo-bot.onrender.com/success?user_id={user_id}",
        cancel_url="https://tuo-bot.onrender.com/cancel",
    )
    return session.url
