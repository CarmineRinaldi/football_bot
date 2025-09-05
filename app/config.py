from __future__ import annotations
import os
from pydantic import BaseModel, Field

class Settings(BaseModel):
    TG_BOT_TOKEN: str = Field(...)
    WEBHOOK_URL: str = Field(...)
    API_FOOTBALL_KEY: str = Field(...)
    STRIPE_SECRET_KEY: str = Field(...)
    STRIPE_ENDPOINT_SECRET: str = Field(...)
    STRIPE_PRICE_2EUR: str = Field(..., description="price_... oppure prod_... per 10 schedine")
    STRIPE_PRICE_VIP: str = Field(..., description="price_... oppure prod_... per VIP mensile")
    DATABASE_URL: str = Field(default="users.db")
    ADMIN_HTTP_TOKEN: str = Field(...)
    FREE_MAX_MATCHES: int = Field(default=5)
    VIP_MAX_MATCHES: int = Field(default=20)

    @property
    def base_url(self) -> str:
        return self.WEBHOOK_URL.rstrip("/")

def get_settings() -> Settings:
    env = {k: os.environ.get(k) for k in [
        "TG_BOT_TOKEN", "WEBHOOK_URL", "API_FOOTBALL_KEY",
        "STRIPE_SECRET_KEY", "STRIPE_ENDPOINT_SECRET",
        "STRIPE_PRICE_2EUR", "STRIPE_PRICE_VIP",
        "DATABASE_URL", "ADMIN_HTTP_TOKEN",
        "FREE_MAX_MATCHES", "VIP_MAX_MATCHES"
    ]}
    if env.get("FREE_MAX_MATCHES"): env["FREE_MAX_MATCHES"] = int(env["FREE_MAX_MATCHES"])  # type: ignore
    if env.get("VIP_MAX_MATCHES"): env["VIP_MAX_MATCHES"] = int(env["VIP_MAX_MATCHES"])     # type: ignore
    return Settings(**env)  # type: ignore

settings = get_settings()
