import { TG_BOT_TOKEN, PLANS } from "./config.js";
import { getUser, saveUser, addSchedina, getSchedine } from "./db.js";
import { getMatches } from "./football.js";

export async function handler(req) {
  const body = await req.json();
  const message = body.message || body.callback_query;

  // gestione /start
  if(message.text === "/start") {
    await fetch(`https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage`, {
      method: "POST",
      body: JSON.stringify({
        chat_id: message.from.id,
        text: "Benvenuto! Scegli un piano",
        reply_markup: {
          inline_keyboard: [
            [{ text: "Free", callback_data: "plan_free" }],
            [{ text: "2€ - 10 schedine", callback_data: "plan_2eur" }],
            [{ text: "VIP 4,99€/mese", callback_data: "plan_vip" }]
          ]
        }
      }),
      headers: { "Content-Type": "application/json" }
    });
  }

  // gestione callback inline
  if(body.callback_query) {
    const data = body.callback_query.data;
    const userId = message.from.id;
    let user = await getUser(userId) || { id: userId, plan: "free" };

    if(data.startsWith("plan_")) {
      user.plan = data.split("_")[1];
      await saveUser(user);
      await fetch(`https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage`, {
        method: "POST",
        body: JSON.stringify({
          chat_id: userId,
          text: "Seleziona il campionato",
          reply_markup: { inline_keyboard: [[{ text:"Serie A", callback_data:"league_SA"}]] }
        }),
        headers: { "Content-Type": "application/json" }
      });
    }

    // altre callback gestite qui...
  }

  return new Response(JSON.stringify({ok:true}), {status:200});
}
