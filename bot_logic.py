import os
import requests
import random
import time
import logging
from datetime import date

from db import get_user, add_ticket, get_user_tickets, decrement_ticket_quota

logger = logging.getLogger(__name__)
API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY")
RAPIDAPI_HOST = "api-football-v1.p.rapidapi.com"

NUM_TICKETS_FREE = 3
NUM_TICKETS_VIP = 15
NUM_TICKETS_PAY = 10
PREDICTIONS_PER_TICKET = 5

# ------------------------
# Utils
# ------------------------
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
        outcome = random.choice(["1","X","2"])
        preds.append(f"{a} vs {b} → {outcome}")
    return preds

# ------------------------
# API Football
# ------------------------
def fetch_matches(category):
    if not API_FOOTBALL_KEY:
        logger.warning("API_FOOTBALL_KEY mancante, uso fittizio")
        return []
    league_map = {
        "Premier League": "39",
        "Serie A": "135",
        "LaLiga": "140",
        "Bundesliga": "78",
        "Ligue 1": "61"
    }
    league_id = league_map.get(category, "39")
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    params = {"league": league_id, "season": "2025"}
    headers = {"X-RapidAPI-Key": API_FOOTBALL_KEY, "X-RapidAPI-Host": RAPIDAPI_HOST}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json().get("response", [])
    except Exception as e:
        logger.error("Errore API-Football: %s", e)
        return []

# ------------------------
# Generazione schedine
# ------------------------
def generate_ticket(user_id, vip_only=False, category=None):
    matches = fetch_matches(category) if category else []
    ticket = []

    if not matches:
        ticket = random.sample(_fake_predictions(category or "Premier League", 100), PREDICTIONS_PER_TICKET)
    else:
        for match in matches[:PREDICTIONS_PER_TICKET]:
            try:
                home = match["teams"]["home"]["name"]
                away = match["teams"]["away"]["name"]
            except KeyError:
                continue
            outcome = random.choice(["1","X","2"])
            ticket.append(f"{home} vs {away} → {outcome}")

    if not vip_only:
        ticket = ticket[:3]

    return {"predictions": ticket, "category": category or "Premier League"}

def generate_daily_tickets_for_user(user_id):
    user = get_user(user_id)
    if not user:
        return []

    plan = user.get("plan", "free")
    categories = user.get("categories") or ["Premier League"]

    n_tickets = NUM_TICKETS_FREE
    vip_only = False
    if plan == "vip":
        n_tickets = NUM_TICKETS_VIP
        vip_only = True
    elif plan == "pay":
        n_tickets = user.get("ticket_quota", NUM_TICKETS_PAY)
        vip_only = True

    today = str(date.today())
    existing = get_user_tickets(user_id, today)
    if existing:
        return existing

    for _ in range(n_tickets):
        category = random.choice(categories)
        ticket = generate_ticket(user_id, vip_only=vip_only, category=category)
        add_ticket(user_id, ticket)
        if plan == "pay":
            decrement_ticket_quota(user_id, 1)
        time.sleep(0.01)

    return get_user_tickets(user_id, today)

# ------------------------
# Invio schedine
# ------------------------
def send_daily_to_user(bot, user_id):
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
        lines = [f"📋 Schedina {idx} ({t.get('category', 'N/A')})"]
        for i, p in enumerate(preds, 1):
            lines.append(f"{i}. {p}")
        try:
            bot.send_message(user_id, "\n".join(lines))
            sent += 1
            time.sleep(0.05)
        except Exception as e:
            logger.error("Errore invio schedina a %s: %s", user_id, e)
            continue
    return sent
