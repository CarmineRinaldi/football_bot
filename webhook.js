const { Telegraf, Markup } = require('telegraf');
const { loadDatabase, saveDatabase, formatSchedina } = require('./utils');
const { getMatches } = require('./footballAPI');

const bot = new Telegraf(process.env.TG_BOT_TOKEN);

bot.start(async ctx => {
  const db = loadDatabase();
  db.users[ctx.from.id] = db.users[ctx.from.id] || { plan: 'free', credits: 0 };
  saveDatabase(db);

  await ctx.reply('Benvenuto! Scegli un piano:', Markup.inlineKeyboard([
    [Markup.button.callback('Free', 'plan_free')],
    [Markup.button.callback('2€ - 10 schedine', 'plan_2eur')],
    [Markup.button.callback('VIP 4,99€/mese', 'plan_vip')]
  ]));
});

bot.on('callback_query', async ctx => {
  const data = ctx.callbackQuery.data;
  await ctx.answerCbQuery();
  const db = loadDatabase();

  if (data.startsWith('plan_')) {
    await ctx.reply('Seleziona il campionato o visualizza le tue schedine', Markup.inlineKeyboard([
      [Markup.button.callback('Serie A', 'league_SA')],
      [Markup.button.callback('Premier League', 'league_PL')],
      [Markup.button.callback('Le mie schedine', 'my_schedules')],
    ]));
  } else if (data.startsWith('league_')) {
    const league = data.split('_')[1];
    const matches = await getMatches(league);
    await ctx.reply('Scegli le partite da inserire nella schedina', Markup.inlineKeyboard(
      matches.slice(0,5).map(m => [Markup.button.callback(`${m.home} vs ${m.away}`, `match_${m.id}`)])
    ));
  } else if (data.startsWith('match_')) {
    const matchId = data.split('_')[1];
    const matches = await getMatches(2025); // fallback
    const match = matches.find(m => m.id == matchId);
    const userSchedine = db.schedine || [];
    userSchedine.push({ user_id: ctx.from.id, created_at: Date.now(), matches: [match], odds: [1.5] });
    db.schedine = userSchedine;
    saveDatabase(db);
    await ctx.reply('Schedina aggiunta!');
  } else if (data === 'my_schedules') {
    const schedine = (db.schedine || []).filter(s => s.user_id === ctx.from.id);
    if (schedine.length === 0) return ctx.reply('Non hai schedine.');
    for (const s of schedine) {
      await ctx.reply(formatSchedina(s.matches, s.odds));
    }
  }
});

// Funzione serverless per Render
module.exports = async function handler(req, res) {
  await bot.handleUpdate(req.body);
  res.json({ ok: true });
};
