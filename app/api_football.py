from __future__ import annotations
import httpx
import time
from typing import Dict, List, Tuple
from .config import settings

API_HOST = "api-football-v1.p.rapidapi.com"
BASE_URL = f"https://{API_HOST}/v3"
HEADERS = {
    "x-rapidapi-host": API_HOST,
    "x-rapidapi-key": settings.API_FOOTBALL_KEY,
}

TOP_LEAGUES: List[Tuple[int, str]] = [
    (39, "Premier League (ENG)"),
    (140, "LaLiga (ESP)"),
    (135, "Serie A (ITA)"),
    (78, "Bundesliga (GER)"),
    (61, "Ligue 1 (FRA)"),
]

async def get_fixtures(league_id: int, days_ahead: int = 7) -> List[Tuple[int, str]]:
    now = int(time.time())
    from_ts = time.strftime("%Y-%m-%d", time.gmtime(now))
    to_ts = time.strftime("%Y-%m-%d", time.gmtime(now + days_ahead*24*3600))
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(
            f"{BASE_URL}/fixtures",
            params={"league": league_id, "season": time.gmtime().tm_year, "from": from_ts, "to": to_ts},
            headers=HEADERS,
        )
        r.raise_for_status()
        data = r.json()
        out: List[Tuple[int, str]] = []
        for it in data.get("response", []):
            fid = it["fixture"]["id"]
            home = it["teams"]["home"]["name"]
            away = it["teams"]["away"]["name"]
            date = it["fixture"].get("date", "")
            out.append((fid, f"{home} vs {away} — {date[:16].replace('T',' ')}"))
        return out

async def get_odds_1x2(fixture_id: int) -> Tuple[Dict[str, float], str, str]:
    """Ritorna (odds, home, away) per il mercato 1X2."""
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(f"{BASE_URL}/odds", params={"fixture": fixture_id}, headers=HEADERS)
        r.raise_for_status()
        data = r.json()
        odds_map: Dict[str, float] = {}
        home = away = ""
        for entry in data.get("response", []):
            for bm in entry.get("bookmakers", []):
                for market in bm.get("bets", []):
                    name = (market.get("name") or "").lower()
                    if "match winner" in name or name == "1x2":
                        for v in market.get("values", []):
                            label = v.get("value")
                            odd = v.get("odd")
                            if not odd:
                                continue
                            if label in ("Home", "1"):
                                odds_map["1"] = float(odd)
                            elif label in ("Draw", "X"):
                                odds_map["X"] = float(odd)
                            elif label in ("Away", "2"):
                                odds_map["2"] = float(odd)
                if set(odds_map.keys()) == {"1", "X", "2"}:
                    break
            if set(odds_map.keys()) == {"1", "X", "2"}:
                break
        # Recupero nomi squadre dal fixture
        fr = await client.get(f"{BASE_URL}/fixtures", params={"id": fixture_id}, headers=HEADERS)
        fr.raise_for_status()
        fdata = fr.json()
        resp = fdata.get("response", [])
        if resp:
            home = resp[0]["teams"]["home"]["name"]
            away = resp[0]["teams"]["away"]["name"]
        return odds_map, home, away
