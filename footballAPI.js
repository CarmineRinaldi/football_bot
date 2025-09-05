const axios = require('axios');

const API_KEY = process.env.API_FOOTBALL_KEY;

async function getMatches(league) {
    const res = await axios.get('https://v3.football.api-sports.io/fixtures', {
        params: { league, season: 2025 },
        headers: { 'x-apisports-key': API_KEY }
    });
    return res.data.response.map(f => ({
        id: f.fixture.id,
        home: f.teams.home.name,
        away: f.teams.away.name,
        odds: f.goals ? f.goals : null
    }));
}

module.exports = { getMatches };
