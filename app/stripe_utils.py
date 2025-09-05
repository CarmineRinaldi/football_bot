from __future__ import annotations
import stripe
import time
from typing import Optional
from .config import settings
from . import database

stripe.api_key = settings.STRIPE_SECRET_KEY

async def _ensure_price_from_product(product_id: str, currency: str, unit_amount: int, recurring: Optional[dict] = None) -> str:
    prod = stripe.Product.retrieve(product_id)
    default_price = prod.get("default_price")
    if default_price:
        return default_price if isinstance(default_price, str) else default_price["id"]
    price = stripe.Price.create(
        product=product_id,
        currency=currency,
        unit_amount=unit_amount,
        recurring=recurring,
    )
    stripe.Product.modify(product_id, default_price=price["id"])
    return price["id"]

async def resolve_price_id(raw: str, pack: bool) -> str:
    if raw.startswith("price_"):
        return raw
    if raw.startswith("prod_"):
        if pack:
            return await _ensure_price_from_product(raw, currency="eur", unit_amount=200, recurring=None)
        else:
            return await _ensure_price_from_product(raw, currency="eur", unit_amount=499, recurring={"interval": "month"})
    raise ValueError("STRIPE_PRICE_* deve essere price_... o prod_...")

async def create_checkout_session(tg_user_id: int, kind: str) -> str:
    if kind not in {"pack", "vip"}:
        raise ValueError("kind non valido")
    price_raw = settings.STRIPE_PRICE_2EUR if kind == "pack" else settings.STRIPE_PRICE_VIP
    price_id = await resolve_price_id(price_raw, pack=(kind == "pack"))
    mode = "payment" if kind == "pack" else "subscription"

    session = stripe.checkout.Session.create(
        mode=mode,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{settings.base_url}/pay/success",
        cancel_url=f"{settings.base_url}/pay/cancel",
        metadata={"tg_user_id": str(tg_user_id), "kind": kind},
    )
    await database.add_stripe_session(tg_user_id, session["id"], mode)
    return session["url"]

async def handle_webhook_event(payload: bytes, sig_header: str) -> str:
    event = stripe.Webhook.construct_event(
        payload=payload,
        sig_header=sig_header,
        secret=settings.STRIPE_ENDPOINT_SECRET,
    )
    etype = event.get("type")
    data = event.get("data", {}).get("object", {})

    if etype == "checkout.session.completed":
        session_id = data.get("id")
        metadata = data.get("metadata", {})
        kind = metadata.get("kind")
        tg_user_id = int(metadata.get("tg_user_id", "0"))
        await database.mark_session_status(session_id, "completed")
        if kind == "pack":
            await database.add_credits(tg_user_id, 10)
        elif kind == "vip":
            until = int(time.time()) + 31*24*3600
            await database.set_vip(tg_user_id, until)

    elif etype == "invoice.payment_succeeded":
        sub = event.get("data", {}).get("object", {})
        metadata = sub.get("metadata", {}) or {}
        tg_user_id = int(metadata.get("tg_user_id", "0")) if metadata.get("tg_user_id") else 0
        if tg_user_id:
            until = int(time.time()) + 31*24*3600
            await database.set_vip(tg_user_id, until)

    return "ok"
