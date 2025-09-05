export async function query(sql, params = []) {
  const databaseUrl = Deno.env.get("DATABASE_URL");
  const client = new WebSocket(databaseUrl); // esempio semplificato, usare Supabase client reale
  // Qui fai query SQL usando il client
  // Ritorna risultato
}

export async function getUser(userId) {
  const res = await query("SELECT * FROM users WHERE id=$1", [userId]);
  return res[0];
}

export async function saveUser(user) {
  await query("INSERT INTO users (id, plan, credits, vip_until) VALUES ($1,$2,$3,$4) ON CONFLICT (id) DO UPDATE SET plan=$2, credits=$3, vip_until=$4",
    [user.id, user.plan, user.credits || 0, user.vip_until || 0]
  );
}

export async function addSchedina(userId, matches, odds) {
  await query("INSERT INTO schedine (user_id, created_at, matches, odds) VALUES ($1,$2,$3,$4)",
    [userId, Date.now(), JSON.stringify(matches), JSON.stringify(odds)]
  );
}

export async function getSchedine(userId) {
  const tenDays = Date.now() - 10*24*60*60*1000;
  await query("DELETE FROM schedine WHERE created_at < $1", [tenDays]);
  const res = await query("SELECT * FROM schedine WHERE user_id=$1", [userId]);
  return res.map(s => ({...s, matches: JSON.parse(s.matches), odds: JSON.parse(s.odds)}));
}
