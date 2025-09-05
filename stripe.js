const Stripe = require('stripe');
const stripe = Stripe(process.env.STRIPE_SECRET_KEY);
const { db, updateUserPlan } = require('./db');

async function handleStripeWebhook(req, res) {
    const sig = req.headers['stripe-signature'];
    let event;
    try {
        event = stripe.webhooks.constructEvent(req.rawBody, sig, process.env.STRIPE_ENDPOINT_SECRET);
    } catch (err) {
        return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    if(event.type === 'checkout.session.completed') {
        const session = event.data.object;
        const userId = parseInt(session.client_reference_id);
        if(session.amount_total === 200) {
            // 2€ = 10 schedine
            const user = db.prepare('SELECT * FROM users WHERE id = ?').get(userId);
            const newCredits = (user.credits || 0) + 10;
            updateUserPlan(userId, 'paid', newCredits);
        } else if(session.amount_total === 499) {
            // VIP 4.99€/mese
            const vip_until = Date.now() + 30*24*60*60*1000;
            updateUserPlan(userId, 'vip', 0, vip_until);
        }
    }

    res.json({received: true});
}

module.exports = { handleStripeWebhook };
