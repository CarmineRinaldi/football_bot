from fastapi import FastAPI, Request
from mine import start, handle_back
from stripe_webhook import handle_stripe_event
import uvicorn

app = FastAPI()

# --------------------------
# Telegram Webhook
# --------------------------
@app.post("/webhook")
async def telegram_webhook(update: Request):
    data = await update.json()
    context = data.get("context", {})  # eventualmente passare context dal payload
    if "message" in data:
        return start(data, context)
    elif "callback_query" in data:
        cb_data = data["callback_query"]["data"]
        last_state = context.get("last_state", None)
        if cb_data == "back":
            return handle_back(data, context, last_state)
        return {"text": f"Callback ricevuto: {cb_data}"}
    return {"text": "Aggiornamento non gestito"}

# --------------------------
# Stripe Webhook
# --------------------------
@app.post("/stripe-webhook")
async def stripe_webhook(req: Request):
    payload = await req.body()
    payload_str = payload.decode("utf-8")  # stripe richiede stringa
    sig_header = req.headers.get("stripe-signature")
    return handle_stripe_event(payload_str, sig_header)

# --------------------------
# Root test
# --------------------------
@app.get("/")
async def root():
    return {"status": "Bot attivo"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
