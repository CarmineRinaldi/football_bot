import os
import stripe
import logging
from db import set_vip, add_tickets

# --- Config logging ---
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Chiavi Stripe ---
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
endpoint_secret = os.environ.get("STRIPE_ENDPOINT_SECRET")

if not stripe.api_key or not endpoint_secret:
    logger.error("Variabili STRIPE_SECRET_KEY o STRIPE_ENDPOINT_SECRET mancanti!")
    exit(1)

# --- Creazione sessione Stripe per VIP ---
def create_vip_checkout_session(user_id):
    """
    Crea una sessione Stripe per un abbonamento VIP mensile.
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{
                'price': os.environ.get("STRIPE_PRICE_ID_VIP"),
                'quantity': 1,
            }],
            metadata={"user_id": str(user_id)},
            success_url=os.environ.get("SUCCESS_URL", "https://example.com/success"),
            cancel_url=os.environ.get("CANCEL_URL", "https://example.com/cancel")
        )
        return session.url
    except Exception as e:
        logger.error("Errore creazione sessione VIP: %s", e)
        return None

# --- Creazione sessione Stripe per pacchetto ticket ---
def create_ticket_checkout_session(user_id, num_tickets=10):
    """
    Crea una sessione Stripe per acquistare pacchetto di ticket singolo.
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='payment',
            line_items=[{
                'price': os.environ.get("STRIPE_PRICE_ID_TICKET"),
                'quantity': num_tickets,
            }],
            metadata={
                "user_id": str(user_id),
                "num_tickets": str(num_tickets)
            },
            success_url=os.environ.get("SUCCESS_URL", "https://example.com/success"),
            cancel_url=os.environ.get("CANCEL_URL", "https://example.com/cancel")
        )
        return session.url
    except Exception as e:
        logger.error("Errore creazione sessione ticket: %s", e)
        return None

# --- Gestione webhook Stripe ---
def handle_stripe_webhook(payload, sig_header):
    """
    Gestisce tutti gli eventi Stripe.
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

    # --- Evento completamento checkout ---
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('metadata', {}).get('user_id')

        # VIP ricorrente
        if session.get('mode') == 'subscription':
            if user_id:
                try:
                    set_vip(int(user_id), vip_status=1)
                    logger.info("Utente %s impostato VIP", user_id)
                except Exception as e:
                    logger.error("Errore aggiornamento VIP per user %s: %s", user_id, e)
                    return False

        # Pagamento pacchetto ticket singolo
        elif session.get('mode') == 'payment':
            num_tickets = int(session.get('metadata', {}).get('num_tickets', 0))
            if user_id and num_tickets > 0:
                try:
                    add_tickets(int(user_id), num_tickets)
                    logger.info("Utente %s ha ricevuto %d ticket acquistati", user_id, num_tickets)
                except Exception as e:
                    logger.error("Errore aggiunta ticket a user %s: %s", user_id, e)
                    return False
        else:
            logger.warning("Evento Stripe sconosciuto: %s", session.get('mode'))

    return True
