from __future__ import annotations
import asyncio
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse, HTMLResponse, JSONResponse, RedirectResponse
from aiogram.types import Update
from .config import settings
from . import database
from .scheduler import start_cleanup_loop
from .bot import bot, dp
from .stripe_utils import handle_webhook_event

app = FastAPI(title="Football Telegram Bot")

@app.on_event("startup")
async def on_startup():
    await database.connect()
    # Avvio scheduler cleanup in background
    asyncio.create_task(start_cleanup_loop())

@app.on_event("shutdown")
async def on_shutdown():
    await database.close()

@app.get("/.well-known/health", response_class=PlainTextResponse)
async def health():
    return "ok"

# --- Admin: set/delete webhook ---
@app.get("/admin/set-webhook")
async def set_webhook(token: str = Query(...)):
    if token != settings.ADMIN_HTTP_TOKEN:
        raise HTTPException(403, "forbidden")
    ok = await bot.set_webhook(url=f"{settings.base_url}/telegram/webhook", allowed_updates=["message","callback_query"])
    return {"ok": ok}

@app.get("/admin/delete-webhook")
async def delete_webhook(token: str = Query(...)):
    if token != settings.ADMIN_HTTP_TOKEN:
        raise HTTPException(403, "forbidden")
    ok = await bot.delete_webhook()
    return {"ok": ok}

# --- Telegram webhook ---
@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return JSONResponse({"ok": True})

# --- Stripe webhook ---
@app.post("/stripe/webhook", response_class=PlainTextResponse)
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("Stripe-Signature")
    if not sig:
        raise HTTPException(400, "missing signature")
    try:
        res = await handle_webhook_event(payload, sig)
        return res
    except Exception as e:
        raise HTTPException(400, f"invalid payload: {e}")

# --- Simple pages ---
@app.get("/pay/success", response_class=HTMLResponse)
async def pay_success():
    return "<h1>Pagamento completato ✅</h1><p>Torna su Telegram per continuare.</p>"

@app.get("/pay/cancel", response_class=HTMLResponse)
async def pay_cancel():
    return "<h1>Pagamento annullato</h1><p>Nessun addebito è stato effettuato.</p>"
