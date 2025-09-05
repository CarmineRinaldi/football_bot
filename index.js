require('dotenv').config();
const { Telegraf, Markup } = require('telegraf');
const express = require('express');
const { addUser, getUser, addSchedina, getSchedine } = require('./db');
const { getMatches } = require('./footballAPI');
const { handleStripeWebhook } = require('./stripe');
const { autoDelete, formatSchedina } = require('./utils');

const bot = new Telegraf(process.env.TG_BOT_TOKEN);
const app = express();
app.use(express.json());
app.use(express.raw({ type: 'application/json' }));

// Webhook Telegram
bot.telegram.setWebhook(`${process.env.WEBHOOK_URL}/webhook`);

// Start
bot.start(async ctx => {
    addUser(ctx.from.id, ctx.from.username);
    await ctx.reply('Benvenuto! Scegli un piano:', Markup.inlineKeyboard([
        [Markup.button.callback('Free', 'plan_free')],
        [Markup.button.callback('2€ - 10 schedine', 'plan_2eur')],
        [Markup.button.callback('VIP 4,99€/mese', 'plan_vip')]
    ]));
});

// Menu callback
bot.on('callback_query', async ctx => {
    const data = ctx.callbackQuery.data;
    await ctx.answerCbQuery();
    await autoDelete(ctx, ctx.callbackQuery.message.message_id);

    if(data.startsWith('plan_')) {
        await ctx.reply('Seleziona il campionato o visualizza le tue schedine', Markup.inlineKeyboard([
            [Markup.button.callback('Serie A', 'league_SA')],
            [Markup.button.callback('Premier League', 'league_PL')],
            [Markup.button.callback('Le mie schedine', 'my_schedules')],
        ]));
    } else if(data.startsWith('league_')) {
        const league = data.split('_')[1];
        const matches = await getMatches(league);
        await ctx.reply('Scegli le partite da inserire nella schedina', Markup.inlineKeyboard(
            matches.slice(0,5).map(m => [Markup.button.callback(`${m.home} vs ${m.away}`, `match_${m.id}`)])
        ));
    } else if(data.startsWith('match_')) {
        // memorizza schedina per semplicità con 1 match
        const matchId = data.split('_')[1];
        const matches = await getMatches(2025); // esempio, da migliorare
        const match = matches.find(m => m.id == matchId);
        addSchedina(ctx.from.id, [match], [1.5]); // esempio quota fissa
        await ctx.reply('Schedina aggiunta!');
    } else if(data === 'my_schedules') {
        const schedine = getSchedine(ctx.from.id);
        if(schedine.length === 0) return ctx.reply('Non hai schedine.');
        for(const s of schedine){
            await ctx.reply(formatSchedina(s.matches, s.odds));
        }
    }
});

// Express endpoints
app.post('/webhook', (req,res) => bot.handleUpdate(req.body, res));
app.post('/stripe-webhook', handleStripeWebhook);

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => console.log(`Server listening on ${PORT}`));
