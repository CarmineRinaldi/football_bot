# Mock API
def get_leagues():
    return ["Serie A", "Premier League", "La Liga"]

def get_matches(league):
    if league == "Serie A":
        return [{"id": "1", "home": "Juventus", "away": "Inter"}, {"id": "2", "home": "Milan", "away": "Napoli"}]
    elif league == "Premier League":
        return [{"id": "3", "home": "Manchester Utd", "away": "Chelsea"}, {"id": "4", "home": "Arsenal", "away": "Liverpool"}]
    elif league == "La Liga":
        return [{"id": "5", "home": "Real Madrid", "away": "Barcelona"}, {"id": "6", "home": "Atletico", "away": "Sevilla"}]
    return []
