import httpx
from app.utils.config import settings
from app.utils.logger import logger


API_BASE = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": settings.API_FOOTBALL_KEY}


async def fetch_leagues():
url = f"{API_BASE}/leagues"
async with httpx.AsyncClient(timeout=10) as c:
r = await c.get(url, headers=HEADERS)
r.raise_for_status()
return r.json()


async def fetch_fixtures(league_id: int = None, date: str = None):
url = f"{API_BASE}/fixtures"
params = {}
if league_id:
params["league"] = league_id
if date:
params["date"] = date
async with httpx.AsyncClient(timeout=10) as c:
r = await c.get(url, headers=HEADERS, params=params)
r.raise_for_status()
return r.json()


# Semplice heuristics di esempio
def build_schedina_from_fixtures(fixtures_json, max_matches: int = 5):
picks = []
data = fixtures_json.get("response", [])
for f in data[:max_matches]:
home = f["teams"]["home"]["name"]
away = f["teams"]["away"]["name"]
pick = f"{home} vs {away} - Esito: 1X2 (favorito)"
picks.append(pick)
return picks
