import os
import random
import logging
import time
from datetime import date

from db import (
    is_vip_user, add_ticket, get_user_tickets,
    get_user, decrement_ticket_quota
)

logger = logging.getLogger(__name__)

# --- Config ---
API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY")
RAPIDAPI_HOST = "api-football-v1.p.rapidapi.com"

NUM_TICKETS_FREE = int(os.getenv("NUM_TICKETS_FREE", "3"))
NUM_TICKETS_VIP = int(os.getenv("NUM_TICKETS_VIP", "15"))
NUM_TICKETS_PAY = int(os.getenv("NUM_TICKETS_PAY", "10"))
PREDICTIONS_PER_TICKET = int(os.getenv("PREDICTIONS_PER_TICKET", "5"))

# ----------------------------------------
# Utils
# ----------------------------------------
def _fake_predictions(category, n=50):
    teams_by_cat = {
        "Premier League": ["Arsenal","Man City","Man Utd","Chelsea","Liverpool"],
        "Serie A": ["Juventus","Milan","Inter","Roma","Napoli"],
        "LaLiga": ["Real Madrid","Barca","Atletico","Sevilla","Valencia"],
        "Bundesliga": ["Bayern","Dortmund","Leverkusen","RB Leipzig","Schalke"],
        "Ligue 1": ["PSG","Marseille","Lyon","Monaco","Rennes"]
    }
    teams = teams_by_cat.get(category, sum(teams_by_cat.values(), []))
    preds = []
    for _ in range(n):
        a, b = random.sample(teams, 2)
        outcome = random.choice(["1", "X", "2"])
        preds.append(f"{a} vs {b} → {outcome}")
    return preds

# ----------------------------------------
# Generazione schedine
# ----------------------------------------
def generate_ticket(user_id, vip_only=False, category=None):
    """Crea una schedina casuale per l'utente e categoria."""
    # Per semplicità al momento generiamo sempre fake predictions
    ticket = random.sample(
        _fake_predictions(category or "Premier League", 100),
        PREDICTIONS_PER_TICKET
    )
    if not vip_only:
        ticket = ticket[:3]
    return {"predictions": ticket, "category": category or "Premier League"}

def generate_daily_tickets_for_user(user_id):
    """Crea schedine giornaliere secondo piano e categorie."""
    user = get_user(user_id)
    plan = user.get("plan", "free")
    categories = user.get("categories", ["Premier League"])

    if plan == "vip":
        n_tickets = NUM_TICKETS_VIP
        vip_only = True
    elif plan == "pay":
        n_tickets = NUM_TICKETS_PAY
        vip_only = True
    else:
        n_tickets = NUM_TICKETS_FREE
        vip_only = False

    today = str(date.today())
    existing = get_user_tickets(user_id, today)
    if existing:
        return existing

    # Genera ticket
    for i in range(n_tickets):
        category = random.choice(categories)
        ticket = generate_ticket(user_id, vip_only=vip_only, category=category)
        add_ticket(user_id, ticket)
        if plan == "pay":
            decrement_ticket_quota(user_id, 1)
        time.sleep(0.01)

    return get_user_tickets(user_id, today)

# ----------------------------------------
# Invio schedine
# ----------------------------------------
def send_daily_to_user(bot, user_id):
    """Invia le schedine giornaliere all’utente via Telegram."""
    tickets = get_user_tickets(user_id, str(date.today()))
    if not tickets:
        tickets = generate_daily_tickets_for_user(user_id)

    if not tickets:
        bot.send_message(user_id, "⚠️ Nessuna schedina disponibile oggi.")
        return 0

    sent = 0
    for idx, t in enumerate(tickets, 1):
        preds = t.get("predictions", [])
        if not preds:
            continue
        lines = [f"📋 Schedina {idx} ({t.get('category','N/A')})"]
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

    logger.info("Inviate %s schedine a utente %s", sent, user_id)
    return sent
