import stripe
from app.config import STRIPE_SECRET_KEY, STRIPE_PRICE_PACK, STRIPE_PRICE_VIP
from app.db.session import get_db
from app.db.models import User, Credit, Subscription
from datetime import datetime, timedelta

stripe.api_key = STRIPE_SECRET_KEY

def create_pack_checkout(user: User):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price": STRIPE_PRICE_PACK,
            "quantity": 1
        }],
        mode="payment",
        success_url="https://your-success-url.com",
        cancel_url="https://your-cancel-url.com",
        metadata={"user_id": user.id}
    )
    return session

def create_vip_checkout(user: User):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price": STRIPE_PRICE_VIP,
            "quantity": 1
        }],
        mode="subscription",
        success_url="https://your-success-url.com",
        cancel_url="https://your-cancel-url.com",
        metadata={"user_id": user.id}
    )
    return session

def handle_webhook(event, db):
    # Logica avanzata: gestisce pagamenti, aggiunge crediti o attiva VIP
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = int(session["metadata"]["user_id"])
        user = db.query(User).filter(User.id==user_id).first()
        if session["mode"] == "payment":
            # Pack
            credit = db.query(Credit).filter(Credit.user_id==user.id).first()
            if not credit:
                credit = Credit(user_id=user.id, remaining=10)
                db.add(credit)
            else:
                credit.remaining += 10
            db.commit()
        elif session["mode"] == "subscription":
            # VIP
            sub = Subscription(user_id=user.id,
                               stripe_subscription_id=session["subscription"],
                               active=True,
                               current_period_end=datetime.utcnow() + timedelta(days=30))
            user.tier = "vip"
            db.add(sub)
            db.commit()
