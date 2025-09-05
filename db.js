const Database = require('better-sqlite3');
const db = new Database(process.env.DATABASE_URL || 'users.db');

// Creazione tabelle se non esistono
db.prepare(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    plan TEXT,
    credits INTEGER DEFAULT 0,
    vip_until INTEGER DEFAULT 0
)`).run();

db.prepare(`CREATE TABLE IF NOT EXISTS schedine (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    created_at INTEGER,
    matches TEXT,
    odds TEXT
)`).run();

// Funzioni helper
module.exports = {
    db,
    addUser: (id, username) => {
        db.prepare('INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)').run(id, username);
    },
    getUser: (id) => db.prepare('SELECT * FROM users WHERE id = ?').get(id),
    updateUserPlan: (id, plan, credits = 0, vip_until = 0) => {
        db.prepare('UPDATE users SET plan = ?, credits = ?, vip_until = ? WHERE id = ?')
          .run(plan, credits, vip_until, id);
    },
    addSchedina: (user_id, matches, odds) => {
        db.prepare('INSERT INTO schedine (user_id, created_at, matches, odds) VALUES (?, ?, ?, ?)')
          .run(user_id, Date.now(), JSON.stringify(matches), JSON.stringify(odds));
    },
    getSchedine: (user_id) => {
        // Rimuove schedine vecchie >10 giorni
        const tenDays = Date.now() - 10 * 24 * 60 * 60 * 1000;
        db.prepare('DELETE FROM schedine WHERE created_at < ?').run(tenDays);
        return db.prepare('SELECT * FROM schedine WHERE user_id = ?').all(user_id)
                   .map(s => ({...s, matches: JSON.parse(s.matches), odds: JSON.parse(s.odds)}));
    }
};
