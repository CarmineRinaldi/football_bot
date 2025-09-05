async function autoDelete(ctx, msgId, delay = 5000) {
    setTimeout(async () => {
        try { await ctx.deleteMessage(msgId); } catch(e){ }
    }, delay);
}

function formatSchedina(matches, odds) {
    return matches.map((m,i)=>`${m.home} vs ${m.away} | Quote: ${odds[i]}`).join('\n');
}

module.exports = { autoDelete, formatSchedina };
