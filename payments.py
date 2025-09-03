import stripe
from config import STRIPE_SECRET_KEY

stripe.api_key = STRIPE_SECRET_KEY

def create_payment_link(amount, currency="eur"):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': currency,
                'product_data': {'name': 'Pronostici Calcio'},
                'unit_amount': int(amount * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='https://t.me/YourBotUsername?start=success',
        cancel_url='https://t.me/YourBotUsername?start=cancel',
    )
    return session.url
