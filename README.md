# ⚽️ Telegram Football Predictions Bot

Bot Telegram con FastAPI, aiogram v3, Stripe e API-Football.
Piani: Free, Pack 2€ (10 schedine), VIP 4,99€/mese.
Schedine memorizzate 10 giorni, auto-cleanup.

## Deploy su Render (rapido)
1) Fai push di questi file su GitHub.
2) Crea un **Web Service** su Render → collega il repo.
3) Build: `pip install -r requirements.txt`
4) Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5) Health Check: `/.well-known/health`
6) Imposta le **env vars** (vedi `.env.sample`).
7) (Opzionale) Persistent Disk → usa `DATABASE_URL=/data/users.db`.
8) GET `https://<app>/admin/set-webhook?token=<ADMIN_HTTP_TOKEN>` per impostare il webhook Telegram.

## Variabili d’ambiente (nomi)
- ADMIN_HTTP_TOKEN
- API_FOOTBALL_KEY
- DATABASE_URL                (es. users.db o /data/users.db)
- FREE_MAX_MATCHES            (es. 5)
- STRIPE_ENDPOINT_SECRET
- STRIPE_PRICE_2EUR           (price_... o prod_...)
- STRIPE_PRICE_VIP            (price_... o prod_...)
- STRIPE_SECRET_KEY
- TG_BOT_TOKEN
- VIP_MAX_MATCHES             (es. 20)
- WEBHOOK_URL                 (es. https://<service>.onrender.com)

## Comandi utili
- GET `/.well-known/health` → ok
- GET `/admin/set-webhook?token=...`
- GET `/admin/delete-webhook?token=...`

## Sviluppo locale
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
