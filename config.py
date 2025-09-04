import os

ADMIN_HTTP_TOKEN = os.environ.get("ADMIN_HTTP_TOKEN")
API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY")
DB_FILE = os.environ.get("DB_FILE", "users.db")
FREE_MAX_MATCHES = int(os.environ.get("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.environ.get("VIP_MAX_MATCHES", 20))
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PRICE_2EUR = os.environ.get("STRIPE_PRICE_2EUR")
STRIPE_PRICE_VIP = os.environ.get("STRIPE_PRICE_VIP")
STRIPE_ENDPOINT_SECRET = os.environ.get("STRIPE_ENDPOINT_SECRET")
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
