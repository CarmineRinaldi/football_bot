import os
import requests
from datetime import datetime, timedelta

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY, "X-Auth-Token": API_KEY}

# --------------------------
# Cache in memoria
# --------------------------
_leagues_cache = None
_national_cache = None
_matches_cache = {}  # {league_id: {"timestamp": ..., "matches": [...]}}

CACHE_TTL = timedelta(minutes=5)  # cache valido 5 minuti

# --------------------------
# Fetch leghe raw
# --------------------------
def _fetch_leagues_raw():
    try:
        res = requests.get(f"{BASE_URL}/leagues", headers=HEADERS, timeout=10)
        res.raise_for_status()
        return res.json().get("response", [])
    except Exception as e:
        print("Errore fetch leagues:", e)
        return []

# --------------------------
# Leghe con cache
# --------------------------
def get_leagues():
    global _leagues_cache
    now = datetime.utcnow()
    if _leagues_cache and now - _leagues_cache["timestamp"] < CACHE_TTL:
        return _leagues_cache["data"]

    data = _fetch_leagues_raw()
    leagues = []
    seen_ids = set()
    for l in data:
        league = l.get("league", {})
        country = l.get("country", {})
        lid = league.get("id")
        name = league.get("name", "")
        country_name = country.get("name") or country.get("code") or ""
        if lid in seen_ids:
            continue
        seen_ids.add(lid)
        l["display_name"] = f"{name} ({country_name})" if country_name else name
        leagues.append(l)

    leagues.sort(key=lambda x: (x.get("country", {}).get("name") or "", x.get("league", {}).get("name") or ""))
    _leagues_cache = {"timestamp": now, "data": leagues}
    return leagues

# --------------------------
# Nazionali con cache
# --------------------------
def get_national_teams():
    global _national_cache
    now = datetime.utcnow()
    if _national_cache and now - _national_cache["timestamp"] < CACHE_TTL:
        return _national_cache["data"]

    data = _fetch_leagues_raw()
    national_leagues = []
    seen_ids = set()
    for l in data:
        league = l.get("league", {})
        typ = (league.get("type") or "").lower()
        if typ != "national":
            continue
        lid = league.get("id")
        country = l.get("country", {})
        name = league.get("name", "")
        country_name = country.get("name") or country.get("code") or ""
        if lid in seen_ids:
            continue
        seen_ids.add(lid)
        l["display_name"] = f"{name} ({country_name})" if country_name else name
        national_leagues.append(l)

    national_leagues.sort(key=lambda x: (x.get("country", {}).get("name") or "", x.get("league", {}).get("name") or ""))
    _national_cache = {"timestamp": now, "data": national_leagues}
    return national_leagues

# --------------------------
# Partite con cache
# --------------------------
def get_matches(league_id):
    now = datetime.utcnow()
    if league_id in _matches_cache:
        cached = _matches_cache[league_id]
        if now - cached["timestamp"] < CACHE_TTL:
            return cached["matches"]

    try:
        url = f"{BASE_URL}/fixtures?league={league_id}&season={datetime.utcnow().year}"
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        data = res.json().get("response", [])
        _matches_cache[league_id] = {"timestamp": now, "matches": data}
        return data
    except Exception as e:
        print(f"Errore get_matches per lega {league_id}: {e}")
        _matches_cache[league_id] = {"timestamp": now, "matches": []}
        return []

# --------------------------
# Ricerca squadre con cache
# --------------------------
def search_teams(query, type_=None):
    query = query.lower()
    results = []

    leagues = get_leagues() if type_ in (None, "league") else []
    nationals = get_national_teams() if type_ in (None, "national") else []

    for league in leagues + nationals:
        league_id = league["league"]["id"]
        matches = get_matches(league_id)
        for m in matches:
            home = m["teams"]["home"]["name"]
            away = m["teams"]["away"]["name"]
            fixture_id = m["fixture"]["id"]

            if query in home.lower():
                results.append({"team": home, "match_id": fixture_id})
            if query in away.lower():
                results.append({"team": away, "match_id": fixture_id})

    seen = set()
    unique_results = []
    for r in results:
        key = (r["team"], r["match_id"])
        if key not in seen:
            seen.add(key)
            unique_results.append(r)

    return unique_results

# --------------------------
# Filtro per lettera
# --------------------------
def filter_by_letter(items, key_name, letter):
    letter = letter.lower()
    return [i for i in items if i[key_name].lower().startswith(letter)]
