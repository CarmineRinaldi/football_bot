from dotenv import load_dotenv
import os

load_dotenv()

# Telegram
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PRICE_2EUR = os.getenv("STRIPE_PRICE_2EUR")
STRIPE_PRICE_VIP = os.getenv("STRIPE_PRICE_VIP")

# Football API (se usi reale)
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
