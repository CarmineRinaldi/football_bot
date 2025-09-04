import os

# -------------------------------
# Telegram
# -------------------------------
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# -------------------------------
# Database
# -------------------------------
DB_FILE = os.environ.get("DB_FILE", "users.db")

# -------------------------------
# Stripe
# -------------------------------
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET = os.environ.get("STRIPE_ENDPOINT_SECRET")
# ID dei prezzi Stripe per i piani
STRIPE_PRICE_2EUR = os.environ.get("STRIPE_PRICE_2EUR")  # es: 'price_2euro_10pronostici'
STRIPE_PRICE_VIP = os.environ.get("STRIPE_PRICE_VIP")    # es: 'price_vip_10al_giorno'

# -------------------------------
# Football API
# -------------------------------
API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY")

# -------------------------------
# Parametri interni
# -------------------------------
FREE_MAX_MATCHES = int(os.environ.get("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.environ.get("VIP_MAX_MATCHES", 20))

# -------------------------------
# Admin (per API HTTP interne se servono)
# -------------------------------
ADMIN_HTTP_TOKEN = os.environ.get("ADMIN_HTTP_TOKEN")
