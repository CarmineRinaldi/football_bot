import os
import stripe
import logging
from db import set_vip

logger = logging.getLogger(__name__)
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
endpoint_secret = os.environ.get("STRIPE_ENDPOINT_SECRET")

def handle_stripe_webhook(payload, sig_header):
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=endpoint_secret
        )
    except stripe.error.SignatureVerificationError as e:
        logger.error("Errore firma webhook Stripe: %s", e)
        return False
    except Exception as e:
        logger.error("Errore generico webhook Stripe: %s", e)
        return False

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('metadata', {}).get('user_id')
        if user_id:
            try:
                set_vip(int(user_id), vip=1)
                logger.info("Utente %s impostato VIP", user_id)
            except Exception as e:
                logger.error("Errore aggiornamento VIP per user %s: %s", user_id, e)
                return False
    return True
