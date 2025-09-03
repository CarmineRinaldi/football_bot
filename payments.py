import os
import stripe
import logging
from db import set_user_plan

# --- Config logging ---
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Chiavi Stripe ---
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
endpoint_secret = os.environ.get("STRIPE_ENDPOINT_SECRET")

if not stripe.api_key or not endpoint_secret:
    logger.error("Variabili STRIPE_SECRET_KEY o STRIPE_ENDPOINT_SECRET mancanti!")
    raise RuntimeError("Stripe non configurato")

# --- Config prezzi pacchetti ---
PRICE_IDS = {
    "vip": os.environ.get("STRIPE_PRICE_VIP"),    # es: piano VIP mensile
    "pay_10": os.environ.get("STRIPE_PRICE_PAY10")  # es: pacchetto 10 schedine a pagamento
}

if not PRICE_IDS["vip"] or not PRICE_IDS["pay_10"]:
    logger.error("ID prezzi Stripe mancanti!")
    raise RuntimeError("Stripe price IDs mancanti")


# =========================
# Creazione checkout session
# =========================
def create_checkout_session(user_id, plan_type):
    """
    Crea una sessione Stripe Checkout per l’utente.
    plan_type: "vip" o "pay_10"
    """
    price_id = PRICE_IDS.get(plan_type)
    if not price_id:
        logger.error("Plan type non valido: %s", plan_type)
        return None

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[{"price": price_id, "quantity": 1}],
            metadata={"user_id": str(user_id), "plan_type": plan_type},
            success_url=os.environ.get("SUCCESS_URL", "https://yourdomain.com/success"),
            cancel_url=os.environ.get("CANCEL_URL", "https://yourdomain.com/cancel")
        )
        return session.url
    except Exception as e:
        logger.exception("Errore creazione checkout session: %s", e)
        return None


# =========================
# Webhook Stripe
# =========================
def handle_stripe_webhook(payload, sig_header):
    """
    Gestisce i webhook di Stripe.
    Aggiorna DB utenti in base al piano acquistato.
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

    # --- Gestione evento pagamento completato ---
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session.get('metadata', {})
        user_id = int(metadata.get('user_id', 0))
        plan_type = metadata.get('plan_type')

        if not user_id or not plan_type:
            logger.warning("Checkout completato senza user_id o plan_type in metadata!")
            return False

        try:
            if plan_type == "vip":
                # Aggiorna utente VIP
                set_user_plan(user_id, "vip", quota=0)
                logger.info("Utente %s aggiornato a VIP", user_id)
            elif plan_type == "pay_10":
                # Pacchetto 10 schedine: aggiungi quota
                # recuperiamo l'utente per sommare la quota
                from db import get_user
                user = get_user(user_id)
                new_quota = (user.get("ticket_quota", 0) + 10) if user else 10
                set_user_plan(user_id, "pay", quota=new_quota)
                logger.info("Utente %s aggiornato con 10 schedine pay", user_id)
            else:
                logger.warning("Tipo di piano Stripe non gestito: %s", plan_type)
                return False
        except Exception as e:
            logger.error("Errore aggiornamento DB per user %s: %s", user_id, e)
            return False

    return True
