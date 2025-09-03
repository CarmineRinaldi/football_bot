import os
import stripe
import logging
from db import set_user_plan, decrement_ticket_quota

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# =========================
# Chiavi Stripe
# =========================
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
endpoint_secret = os.environ.get("STRIPE_ENDPOINT_SECRET")

if not stripe.api_key or not endpoint_secret:
    logger.error("Variabili STRIPE_SECRET_KEY o STRIPE_ENDPOINT_SECRET mancanti!")
    exit(1)

# =========================
# Crea sessione Stripe per VIP
# =========================
def create_vip_checkout_session(user_id, success_url, cancel_url):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": "Abbonamento VIP"},
                    "unit_amount": 500,  # 5€ ad esempio
                },
                "quantity": 1
            }],
            metadata={"user_id": str(user_id), "plan": "vip"},
            success_url=success_url,
            cancel_url=cancel_url
        )
        return session.url
    except Exception as e:
        logger.error("Errore creazione sessione VIP Stripe: %s", e)
        return None

# =========================
# Crea sessione Stripe per Pacchetto Pay
# =========================
def create_pay_package_session(user_id, success_url, cancel_url, quantity=10):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": f"Pacchetto {quantity} schedine"},
                    "unit_amount": 200,  # 2€ in centesimi
                },
                "quantity": 1
            }],
            metadata={"user_id": str(user_id), "plan": "pay", "quota": quantity},
            success_url=success_url,
            cancel_url=cancel_url
        )
        return session.url
    except Exception as e:
        logger.error("Errore creazione sessione Pay Stripe: %s", e)
        return None

# =========================
# Gestione webhook Stripe
# =========================
def handle_stripe_webhook(payload, sig_header):
    """
    Gestisce webhook Stripe.
    Imposta VIP o aumenta quota Pay a seconda del metadata.
    """
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=endpoint_secret
        )
        logger.info("Evento Stripe ricevuto: %s", event['type'])
    except stripe.error.SignatureVerificationError as e:
        logger.error("Errore firma webhook Stripe: %s", e)
        return False
    except Exception as e:
        logger.error("Errore generico webhook Stripe: %s", e)
        return False

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('metadata', {}).get('user_id')
        plan = session.get('metadata', {}).get('plan')

        if not user_id or not plan:
            logger.warning("Checkout completato senza user_id o plan nel metadata!")
            return False

        try:
            user_id = int(user_id)
            if plan == "vip":
                set_user_plan(user_id, "vip")
                logger.info("Utente %s impostato VIP via Stripe", user_id)
            elif plan == "pay":
                quota = int(session.get('metadata', {}).get('quota', 10))
                decrement_ticket_quota(user_id, -quota)  # incremento quota
                set_user_plan(user_id, "pay")
                logger.info("Utente %s acquistato pacchetto %s schedine", user_id, quota)
            else:
                logger.warning("Plan non riconosciuto: %s", plan)
                return False
        except Exception as e:
            logger.error("Errore aggiornamento utente %s via Stripe: %s", user_id, e)
            return False

    return True
