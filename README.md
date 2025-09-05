# Football Telegram Bot - Avanzato

Bot Telegram professionale per pronostici calcio con gestione Stripe (Pack/VIP), API-Football e scheduler giornaliero.

## Requisiti
- Account Render o altro hosting
- Database Postgres
- Stripe (Price ID per Pack e VIP)
- API-Football Key

## Installazione
1. Clona repo
2. Copia `.env.example` in `.env` e inserisci le chiavi
3. `pip install -r requirements.txt`
4. `python app/db/init_db.py`
5. Avvia: `uvicorn app.main:app --reload`

## Deploy
- Usa Render: build `pip install -r requirements.txt`, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Imposta webhook Telegram:  
`https://api.telegram.org/bot<TG_BOT_TOKEN>/setWebhook?url=${WEBHOOK_PUBLIC_BASE}${WEBHOOK_PATH}`
- Stripe webhook: `${WEBHOOK_PUBLIC_BASE}/stripe/webhook`
