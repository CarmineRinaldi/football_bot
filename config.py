import os
import sys

# ⚽ Limiti utilizzo piani
FREE_MAX_MATCHES: int = int(os.getenv("FREE_MAX_MATCHES", "5"))
VIP_MAX_MATCHES: int = int(os.getenv("VIP_MAX_MATCHES", "20"))

# 🗄️ Database
DATABASE_URL: str = os.getenv("DATABASE_URL", "users.db")

# 📡 API esterne
API_FOOTBALL_KEY: str | None = os.getenv("API_FOOTBALL_KEY")

# 🤖 Telegram
TG_BOT_TOKEN: str | None = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL: str | None = os.getenv("WEBHOOK_URL")

# 💳 Stripe
STRIPE_SECRET_KEY: str | None = os.getenv("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET: str | None = os.getenv("STRIPE_ENDPOINT_SECRET")
STRIPE_PRICE_2EUR: str | None = os.getenv("STRIPE_PRICE_2EUR")
STRIPE_PRICE_VIP: str | None = os.getenv("STRIPE_PRICE_VIP")

# 🔒 Controlli critici: senza token e webhook il bot non può avviarsi
if not TG_BOT_TOKEN or not WEBHOOK_URL:
    sys.exit("❌ ERRORE: Variabili d'ambiente TG_BOT_TOKEN e WEBHOOK_URL sono obbligatorie!")
