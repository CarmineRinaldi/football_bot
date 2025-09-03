import os

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "8488759682:AAEdaxTctJ1Yy21fIhXqIl9Y3IJf2VdJnC8")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "0f929a8958mshfcc5b8a323e18dap198234jsnfbbdc1865d64")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "YOUR_STRIPE_SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")  # puoi usare PostgreSQL su Render
