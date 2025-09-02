import os
import stripe
import logging
from db import set_vip

# --- Config logging ---
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Chiavi Stripe ---
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
endpoint_secret = os.environ.get("STRIPE_ENDPOINT_SECRET")

if not stripe.api_key or not endpoint_secret:
    logger.error("Variabili STRIPE_SECRET_KEY o STRIPE_ENDPOINT_SECRET mancanti!")
    exit(1)

def handle_stripe_webhook(payload, sig_header):
    """
    Gestisce i webhook di Stripe.
    Ritorna True se l'evento viene processato correttamente, False altrimenti.
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

    # --- Gestione evento specifico ---
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Prendi user_id dal metadata
        user_id = session.get('metadata', {}).get('user_id')
        if user_id:
            try:
                set_vip(int(user_id), vip=1)
                logger.info("Utente %s impostato VIP", user_id)
            except Exception as e:
                logger.error("Errore aggiornamento VIP per user %s: %s", user_id, e)
                return False
        else:
            logger.warning("Checkout completato senza user_id in metadata!")

    # Qui puoi aggiungere altri tipi di eventi se vuoi
    # elif event['type'] == 'payment_intent.succeeded':
    #     ...

    return True
