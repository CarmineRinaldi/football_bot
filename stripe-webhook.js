const Stripe = require('stripe');
const stripe = Stripe(process.env.STRIPE_SECRET_KEY);
const { loadDatabase, saveDatabase } = require('./utils');

module.exports = async function handler(req, res) {
  const sig = req.headers['stripe-signature'];
  let event;
  try {
    event = stripe.webhooks.constructEvent(req.rawBody, sig, process.env.STRIPE_ENDPOINT_SECRET);
  } catch (err) {
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  const db = loadDatabase();

  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;
    const userId = session.client_reference_id;
    const user = db.users[userId] || { plan: 'free', credits: 0 };

    if (session.amount_total === 200) {
      // 2€ = 10 schedine
      user.plan = 'paid';
      user.credits = (user.credits || 0) + 10;
    } else if (session.amount_total === 499) {
      // VIP 4.99€/mese
      user.plan = 'vip';
      user.vip_until = Date.now() + 30*24*60*60*1000;
    }
    db.users[userId] = user;
    saveDatabase(db);
  }

  res.json({ received: true });
};
