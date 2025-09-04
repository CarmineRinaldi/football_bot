import stripe
from config import STRIPE_SECRET_KEY, STRIPE_PRICE_2EUR, STRIPE_PRICE_VIP

stripe.api_key = STRIPE_SECRET_KEY

def create_checkout_session(user_id, price_type):
    price_id = STRIPE_PRICE_2EUR if price_type == "2eur" else STRIPE_PRICE_VIP
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{'price': price_id, 'quantity': 1}],
        mode='payment',
        success_url=f"https://tuo-bot.onrender.com/success?user_id={user_id}",
        cancel_url="https://tuo-bot.onrender.com/cancel"
    )
    return session.url
