import { STRIPE_SECRET_KEY, STRIPE_ENDPOINT_SECRET } from "./config.js";
import { getUser, saveUser } from "./db.js";

export async function handler(req) {
  const sig = req.headers.get("stripe-signature");
  const body = await req.text();
  const stripe = Stripe(STRIPE_SECRET_KEY);
  let event;
  try { event = stripe.webhooks.constructEvent(body, sig, STRIPE_ENDPOINT_SECRET); }
  catch(e) { return new Response(`Webhook Error: ${e.message}`, {status:400}); }

  if(event.type==="checkout.session.completed") {
    const session = event.data.object;
    const userId = session.client_reference_id;
    let user = await getUser(userId) || { id:userId, plan:"free" };

    if(session.amount_total === 200) user.plan="paid";
    else if(session.amount_total === 499) user.plan="vip";

    await saveUser(user);
  }

  return new Response(JSON.stringify({received:true}), {status:200});
}
