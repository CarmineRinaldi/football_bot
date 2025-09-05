export const TG_BOT_TOKEN = Deno.env.get("TG_BOT_TOKEN");
export const WEBHOOK_URL = Deno.env.get("WEBHOOK_URL");
export const API_FOOTBALL_KEY = Deno.env.get("API_FOOTBALL_KEY");
export const STRIPE_SECRET_KEY = Deno.env.get("STRIPE_SECRET_KEY");
export const STRIPE_ENDPOINT_SECRET = Deno.env.get("STRIPE_ENDPOINT_SECRET");

export const FREE_MAX_MATCHES = 5;
export const VIP_MAX_MATCHES = 20;

export const PLANS = {
  free: { name: "Free", maxMatches: FREE_MAX_MATCHES },
  paid: { name: "2€ - 10 schedine", maxMatches: FREE_MAX_MATCHES, credits: 10 },
  vip: { name: "VIP 4,99€/mese", maxMatches: VIP_MAX_MATCHES }
};
