// Funzioni comuni
const fs = require('fs');

function loadDatabase() {
  return JSON.parse(fs.readFileSync('./database.json'));
}

function saveDatabase(db) {
  fs.writeFileSync('./database.json', JSON.stringify(db, null, 2));
}

function formatSchedina(matches, odds) {
  return matches.map((m, i) => `${m.home} vs ${m.away} | Quote: ${odds[i]}`).join('\n');
}

function autoDelete(ctx, msgId, delay = 5000) {
  setTimeout(async () => {
    try { await ctx.deleteMessage(msgId); } catch (e) {}
  }, delay);
}

module.exports = { loadDatabase, saveDatabase, formatSchedina, autoDelete };
