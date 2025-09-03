import stripe
from config import STRIPE_API_KEY
from database import update_user, get_user
import json

stripe.api_key = STRIPE_API_KEY

def get_daily_tips(user_id):
    user = get_user(user_id)
    if user["plan"] == "vip":
        return 10
    elif user["credits"] > 0:
        return min(user["credits"], 1)
    else:
        return 0

def decrement_credits(user_id, amount=1):
    user = get_user(user_id)
    new_credits = max(0, user["credits"] - amount)
    update_user(user_id, credits=new_credits)
    return new_credits

def load_tips():
    with open("pronostici.json", "r") as f:
        return json.load(f)

# --- Stripe ---
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
