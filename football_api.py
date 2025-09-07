# football_api.py — versione aggiornata
import os
import requests
from datetime import datetime

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"
# includiamo entrambi i nomi di header per compatibilità
HEADERS = {"x-apisports-key": API_KEY, "X-Auth-Token": API_KEY}

def _fetch_leagues_raw():
    """Chiamata centrale per prendere /leagues e gestire errori."""
    try:
        res = requests.get(f"{BASE_URL}/leagues", headers=HEADERS, timeout=10)
        res.raise_for_status()
        return res.json().get("response", [])
    except Exception as e:
        print("Errore fetch leagues:", e)
        return []

def get_leagues():
    """
    Restituisce una lista di leghe 'di club' deduplicate e con display_name.
    Non filtra eccessivamente sul tipo per evitare liste vuote.
    """
    data = _fetch_leagues_raw()
    seen_ids = set()
    seen_name_country = set()
    leagues = []

    for l in data:
        league = l.get("league", {})
        country = l.get("country", {})
        lid = league.get("id")
        name = league.get("name", "")
        country_name = country.get("name") or country.get("code") or ""

        # deduplicate per id o per (nome, paese)
        key_name_country = (name.strip().lower(), country_name.strip().lower())
        if lid in seen_ids or key_name_country in seen_name_country:
            continue

        seen_ids.add(lid)
        seen_name_country.add(key_name_country)

        # aggiungiamo un display_name utile per i bottoni (es. "Serie A (Italy)")
        l["display_name"] = f"{name} ({country_name})" if country_name else name

        # opzionale: preferiamo leghe con seasons non vuote (ma non le escludiamo rigidamente)
        seasons = l.get("seasons", [])
        if seasons:
            leagues.append(l)
        else:
            # aggiungiamo comunque come fallback
            leagues.append(l)

    # ordiniamo per paese/ nome per avere ordine consistente
    leagues.sort(key=lambda x: (x.get("country", {}).get("name") or "", x.get("league", {}).get("name") or ""))
    return leagues

def get_national_teams():
    """
    Restituisce competizioni nazionali / coppe deduplicate.
    """
    data = _fetch_leagues_raw()
    seen_ids = set()
    seen_name_country = set()
    national_leagues = []

    for l in data:
        league = l.get("league", {})
        country = l.get("country", {})
        lid = league.get("id")
        name = league.get("name", "")
        typ = (league.get("type") or "").lower()
        country_name = country.get("name") or country.get("code") or ""
        key_name_country = (name.strip().lower(), country_name.strip().lower())

        # prendiamo se sembra una competizione nazionale/cup o comunque ha country
        if not (typ in ["national", "cup"] or country_name):
            # lasciare un po' largo il filtro per non perdere dati utili
            pass

        if lid in seen_ids or key_name_country in seen_name_country:
            continue

        seen_ids.add(lid)
        seen_name_country.add(key_name_country)

        l["display_name"] = f"{name} ({country_name})" if country_name else name
        national_leagues.append(l)

    national_leagues.sort(key=lambda x: (x.get("country", {}).get("name") or "", x.get("league", {}).get("name") or ""))
    return national_leagues

def get_matches(league_id):
    """
    Prova a recuperare le fixtures per una lega:
    1) senza season (più generico),
    2) fallback su anno corrente / anno precedente / anno successivo.
    Ritorna lista di match (puoi filtrare date/partite future lato caller).
    """
    try:
        # 1) prova senza season
        url = f"{BASE_URL}/fixtures?league={league_id}"
        res = requests.get(url, headers=HEADERS, timeout=10)
        # debug rapido
        print(f"GET {url} -> {res.status_code}")
        res.raise_for_status()
        data = res.json().get("response", [])
        if data:
            print(f"Found {len(data)} matches for league {league_id} (no season filter).")
            return data

        # 2) fallback su anni vicini
        year = datetime.utcnow().year
        for s in (year, year-1, year+1):
            url_s = f"{BASE_URL}/fixtures?league={league_id}&season={s}"
            res = requests.get(url_s, headers=HEADERS, timeout=10)
            print(f"GET {url_s} -> {res.status_code}")
            res.raise_for_status()
            data = res.json().get("response", [])
            if data:
                print(f"Found {len(data)} matches for league {league_id} season {s}.")
                return data

        print(f"No matches found for league {league_id} after all fallbacks.")
        return []
    except Exception as e:
        print(f"Errore get_matches per lega {league_id}: {e}")
        return []
