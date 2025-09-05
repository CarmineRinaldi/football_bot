# Football Bot Serverless

## Deploy su Render
1. Carica la cartella su GitHub.
2. Crea servizio **Web Service** o **Serverless Function** su Render.
3. Imposta runtime compatibile con Deno o serverless JS.
4. Configura variabili d'ambiente:
   - TG_BOT_TOKEN
   - WEBHOOK_URL
   - API_FOOTBALL_KEY
   - STRIPE_SECRET_KEY
   - STRIPE_ENDPOINT_SECRET
   - DATABASE_URL (PostgreSQL/Supabase)
5. Punta il webhook Telegram a `WEBHOOK_URL`.
6. Stripe webhook a `stripe.js`.
