import { API_FOOTBALL_KEY } from "./config.js";

export async function getMatches(league) {
  const res = await fetch(`https://v3.football.api-sports.io/fixtures?league=${league}&season=2025`, {
    headers: { "x-apisports-key": API_FOOTBALL_KEY }
  });
  const data = await res.json();
  return data.response.map(f => ({
    id: f.fixture.id,
    home: f.teams.home.name,
    away: f.teams.away.name,
    odds: f.goals ? f.goals : 1.5
  }));
}
