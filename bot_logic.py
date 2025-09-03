import requests
import os
import random
import logging
import time
from datetime import date

from db import is_vip_user, add_ticket, get_user_tickets

logger = logging.getLogger(__name__)

API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY")
RAPIDAPI_HOST = "api-football-v1.p.rapidapi.com"

# Configurazioni (modificabili via variabili d’ambiente)
NUM_TICKETS_FREE = int(os.getenv("NUM_TICKETS_FREE", "10"))
NUM_TICKETS_VIP = int(os.getenv("NUM_TICKETS_VIP", "15"))
PREDICTIONS_PER_TICKET = int(os.getenv("PREDICTIONS_PER_TICKET", "5"))

# ----------------------------------------
# Utils
# ----------------------------------------
def _fake_predictions(n=50):
    """Fallback in caso API non disponibile."""
    teams = [
        "Arsenal","Man City","Man Utd","Chelsea","Liverpool","Tottenham",
        "Leicester","Everton","West Ham","Newcastle","Wolves","Aston Villa",
        "Brighton","Crystal Palace","Brentford","Bournemouth","Fulham","Nottingham"
    ]
    preds = []
    for _ in range(n):
        a, b = random.sample(teams, 2)
        outcome = random.choice(["1", "X", "2"])
        preds.append(f"{a} vs {b} → {outcome}")
    return preds

# ----------------------------------------
# API Football
# ----------------------------------------
def fetch_matches():
    """Recupera partite da API Football (Premier League come esempio)."""
    if not API_FOOTBALL_KEY:
        logger.warning("API_FOOTBALL_KEY mancante: uso pronostici fittizi.")
        return []

    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    params = {"league": "39", "season": "2025"}
    headers = {
        "X-RapidAPI-Key": API_FOOTBALL_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("response", [])
    except Exception as e:
        logger.error("Errore API-Football: %s", e)
        return []

# ----------------------------------------
# Generazione schedine
# ----------------------------------------
def generate_ticket(vip_only=False, max_matches=PREDICTIONS_PER_TICKET):
    """Crea una schedina casuale."""
    matches = fetch_matches()
    ticket = []

    if not matches:
        # se API vuota, uso fallback
        ticket = random.sample(_fake_predictions(100), max_matches)
    else:
        for match in matches[:max_matches]:
            try:
                home = match["teams"]["home"]["name"]
                away = match["teams"]["away"]["name"]
            except KeyError:
                continue
            outcome = random.choice(["1", "X", "2"])
            ticket.append(f"{home} vs {away} → {outcome}")

    # Se non è VIP mostro solo 3 pronostici
    if not vip_only:
        ticket = ticket[:3]

    return ticket

def generate_daily_tickets_for_user(user_id, vip=False):
    """Crea schedine giornaliere e le salva nel DB (se non esistono già)."""
    today = str(date.today())
    existing = get_user_tickets(user_id, today)
    if existing:
        logger.debug("Schedine già presenti per utente %s", user_id)
        return existing

    n_tickets = NUM_TICKETS_VIP if vip else NUM_TICKETS_FREE
    for i in range(n_tickets):
        ticket = generate_ticket(vip_only=vip)
        # Salvo sempre come dict con chiave "predictions"
        add_ticket(user_id, {
            "predictions": ticket,
            "date": today,
            "meta": {"index": i, "vip": int(vip)}
        })
        time.sleep(0.01)  # piccola pausa per non bloccare SQLite

    return get_user_tickets(user_id, today)

# ----------------------------------------
# Invio schedine
# ----------------------------------------
def send_daily_to_user(bot, user_id):
    """Invia le schedine giornaliere all’utente via Telegram."""
    vip = is_vip_user(user_id)
    today = str(date.today())

    tickets = get_user_tickets(user_id, today)
    if not tickets:
        tickets = generate_daily_tickets_for_user(user_id, vip)

    if not tickets:
        bot.send_message(user_id, "⚠️ Nessuna schedina disponibile oggi.")
        return 0

    sent = 0
    for idx, t in enumerate(tickets, 1):
        # Estraggo pronostici in modo sicuro
        preds = t.get("predictions") or t.get("data", {}).get("predictions", [])
        if not preds:
            continue
        lines = [f"📋 Schedina {idx}"]
        for i, p in enumerate(preds, 1):
            lines.append(f"{i}. {p}")
        txt = "\n".join(lines)
        try:
            bot.send_message(user_id, txt)
            sent += 1
            time.sleep(0.05)
        except Exception as e:
            logger.error("Errore invio schedina a %s: %s", user_id, e)
            continue

    logger.info("Inviate %s schedine a utente %s (VIP=%s)", sent, user_id, vip)
    return sent
