import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from bot_logic import start, show_main_menu, show_leagues, show_matches, create_ticket
from football_api import get_leagues, get_matches
from stripe_webhook import handle_stripe_event

app = FastAPI()

# ROUTE PER IL BOT (TELEGRAM)
@app.post("/telegram_webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    # Qui puoi gestire i messaggi in arrivo
    # ad esempio chiamando la funzione start() o altre funzioni del bot
    return JSONResponse({"status": "ok"})

# ROUTE PER FOOTBALL
@app.get("/leagues")
async def leagues():
    leagues_data = get_leagues()
    return JSONResponse(leagues_data)

@app.get("/matches")
async def matches(league_id: int):
    matches_data = get_matches(league_id)
    return JSONResponse(matches_data)

# ROUTE PER STRIPE WEBHOOK
@app.post("/stripe_webhook")
async def stripe_webhook(req: Request):
    payload = await req.body()
    sig_header = req.headers.get("stripe-signature")
    response = handle_stripe_event(payload, sig_header)
    return JSONResponse(response)

# ROUTE DI TEST PRINCIPALE
@app.get("/")
async def root():
    return {"message": "Server attivo"}

# Se vuoi eseguire il bot all'avvio del server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)
