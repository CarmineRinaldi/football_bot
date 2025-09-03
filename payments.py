import os
import stripe
import logging
from db import set_plan

logger = logging.getLogger(__name__)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
endpoint_secret = os.environ.get("STRIPE_ENDPOINT_SECRET")

if not stripe.api_key or not endpoint_secret:
    logger.error("Variabili STRIPE_SECRET_KEY o STRIPE_ENDPOINT_SECRET mancanti!")
    exit(1)

def handle_stripe_webhook(payload, sig_header):
    """
    Gestisce i webhook di Stripe.
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
        plan = session.get('metadata', {}).get('plan', 'pay')
        quota = session.get('metadata', {}).get('ticket_quota', 10)

        if user_id:
            try:
                set_plan(int(user_id), plan=plan, ticket_quota=int(quota))
                logger.info("Utente %s impostato plan=%s ticket_quota=%s", user_id, plan, quota)
            except Exception as e:
                logger.error("Errore aggiornamento plan per user %s: %s", user_id, e)
                return False
        else:
            logger.warning("Checkout completato senza user_id in metadata!")

    return True
