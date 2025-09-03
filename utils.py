import stripe
from config import STRIPE_API_KEY
from database import update_user, get_user

stripe.api_key = STRIPE_API_KEY

def create_stripe_checkout(user_id, plan):
    if plan == "10_credits":
        price = 200
    elif plan == "vip":
        price = 500
    else:
        return None

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {'name': f'Pacchetto {plan}'},
                'unit_amount': price,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=f'https://t.me/IL_TUO_BOT_USERNAME?start=success_{user_id}_{plan}',
        cancel_url=f'https://t.me/IL_TUO_BOT_USERNAME?start=cancel',
    )
    return session.url

def process_success(user_id, plan):
    if plan == "10_credits":
        update_user(user_id, credits=10, plan="paid")
    elif plan == "vip":
        update_user(user_id, credits=10, plan="vip")
