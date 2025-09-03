import os
import requests
import random
import logging
import time
from datetime import date

from db import is_vip_user, get_user, add_ticket, get_user_tickets, mark_ticket_used

logger = logging.getLogger(__name__)

API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY")
RAPIDAPI_HOST = "api-football-v1.p.rapidapi.com"

# Configurazioni
NUM_TICKETS_FREE = int(os.getenv("NUM_TICKETS_FREE", "10"))
NUM_TICKETS_VIP = int(os.getenv("NUM_TICKETS_VIP", "15"))
PREDICTIONS_PER_TICKET = int(os.getenv("PREDICTIONS_PER_TICKET", "5"))

# ----------------------------------------
# Categorie principali (campionati)
# ----------------------------------------
def get_available_categories():
    return [
        "Premier League",
        "Serie A",
        "La Liga",
        "Bundesliga",
        "Ligue 1",
        "Champions League",
        "Europa League"
    ]

# ----------------------------------------
# Utils fallback pronostici
# ----------------------------------------
def _fake_predictions(n=50):
    teams = [
        "Arsenal","Man City","Man Utd","Chelsea","Liverpool","Tottenham",
        "Leicester","Everton","West Ham","Newcastle","Wolves","Aston Villa",
        "Brighton","Crystal Palace","Brentford","Bournemouth","Fulham","Nottingham",
        "Juventus","Inter","Milan","Roma","Napoli","Lazio","Fiorentina","Atalanta",
        "Barcelona","Real Madrid","Atletico","Sevilla","Valencia",
        "Bayern","Dortmund","Leverkusen","RB Leipzig"
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
def fetch_matches(category="Premier League"):
    """Recupera partite da API Football in base alla categoria."""
    if not API_FOOTBALL_KEY:
        logger.warning("API_FOOTBALL_KEY mancante: uso pronostici fittizi.")
        return []

    league_map = {
        "Premier League": 39,
        "Serie A": 135,
        "La Liga": 140,
        "Bundesliga": 78,
        "Ligue 1": 61,
        "Champions League": 2,
        "Europa League": 3
    }
    league_id = league_map.get(category, 39)
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    params = {"league": str(league_id), "season": "2025"}
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
# Generazione schedina
# ----------------------------------------
def generate_ticket(user_id, category="Premier League", vip_only=False, max_matches=PREDICTIONS_PER_TICKET):
    matches = fetch_matches(category)
    ticket = []

    if not matches:
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

    if not vip_only:
        ticket = ticket[:3]  # Free users vedono solo 3 pronostici

    add_ticket(user_id, ticket, category, vip_only=int(vip_only))
    return ticket

# ----------------------------------------
# Creazione schedine giornaliere per utente
# ----------------------------------------
def generate_daily_tickets_for_user(user_id):
    user = get_user(user_id)
    if not user:
        logger.warning("Utente %s non trovato.", user_id)
        return []

    plan = user["plan"]
    categories = user["categories"] or get_available_categories()
    tickets_to_generate = 0

    if plan == "vip":
        tickets_to_generate = NUM_TICKETS_VIP
    elif plan == "free":
        tickets_to_generate = NUM_TICKETS_FREE
    elif plan == "pay_per_ticket":
        tickets_to_generate = user["ticket_balance"]
        if tickets_to_generate == 0:
            logger.info("Utente %s senza ticket disponibili.", user_id)
            return []

    tickets = []
    for i in range(tickets_to_generate):
        category = random.choice(categories)
        vip_flag = plan == "vip"
        ticket = generate_ticket(user_id, category, vip_only=vip_flag)
        tickets.append({
            "category": category,
            "ticket": ticket,
            "vip_only": vip_flag
        })
        # decrementa saldo per pay-per-ticket
        if plan == "pay_per_ticket":
            from db import set_plan
            set_plan(user_id, "pay_per_ticket", add_tickets=-1)
        time.sleep(0.01)

    return tickets

# ----------------------------------------
# Invio schedine giornaliere
# ----------------------------------------
def send_daily_to_user(bot, user_id):
    user = get_user(user_id)
    if not user:
        logger.warning("Utente %s non trovato.", user_id)
        return 0

    tickets = generate_daily_tickets_for_user(user_id)
    if not tickets:
        bot.send_message(user_id, "⚠️ Nessuna schedina disponibile oggi.")
        return 0

    sent_count = 0
    for idx, t in enumerate(tickets, 1):
        lines = [f"📋 Schedina {idx} ({t['category']})"]
        for i, p in enumerate(t["ticket"], 1):
            lines.append(f"{i}. {p}")
        txt = "\n".join(lines)
        try:
            bot.send_message(user_id, txt)
            sent_count += 1
            time.sleep(0.05)
        except Exception as e:
            logger.error("Errore invio schedina a %s: %s", user_id, e)

    logger.info("Inviate %s schedine a utente %s", sent_count, user_id)
    return sent_count
