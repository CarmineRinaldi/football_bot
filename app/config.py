import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_PUBLIC_BASE = os.getenv("WEBHOOK_PUBLIC_BASE")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/bot/webhook")
WEBHOOK_URL = (WEBHOOK_PUBLIC_BASE or "") + (WEBHOOK_PATH or "")

API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET")
STRIPE_PRICE_PACK = os.getenv("STRIPE_PRICE_PACK")
STRIPE_PRICE_VIP = os.getenv("STRIPE_PRICE_VIP")

DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_HTTP_TOKEN = os.getenv("ADMIN_HTTP_TOKEN")

FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Europe/Rome")
