import os
from pydantic import BaseSettings


class Settings(BaseSettings):
TG_BOT_TOKEN: str
ADMIN_HTTP_TOKEN: str
API_FOOTBALL_KEY: str
STRIPE_SECRET_KEY: str
STRIPE_ENDPOINT_SECRET: str
STRIPE_PRICE_2EUR: str
STRIPE_PRICE_VIP: str
DATABASE_URL: str
WEBHOOK_PUBLIC_BASE: str
FREE_MAX_MATCHES: int = 5
VIP_MAX_MATCHES: int = 20
FREE_COOLDOWN_HOURS: int = 24
TIMEZONE_DEFAULT: str = "Europe/Rome"


class Config:
env_file = ".env"
env_file_encoding = 'utf-8'


settings = Settings()
