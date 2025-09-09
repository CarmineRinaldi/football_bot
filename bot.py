import sqlite3
import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ---------------- VARIABILI ----------------
DB_PATH = os.getenv("DATABASE_URL", "users.db")
FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Tabella utenti
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            is_vip INTEGER DEFAULT 0
        )
    """)
    # Tabella cronologia partite
    c.execute("""
        CREATE TABLE IF NOT EXISTS matches_history (
            match_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            score TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    conn.commit()
    conn.close()

# ---------------- UTILITY ----------------
def get_match_count(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM matches_history WHERE user_id = ?", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def is_vip(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT is_vip FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row and row[0] == 1

# ---------------- COMANDI ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"Ciao {username}! Benvenuto nel Football Bot ⚽")

async def match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    matches_played = get_match_count(user_id)
    vip = is_vip(user_id)
    max_matches = VIP_MAX_MATCHES if vip else FREE_MAX_MATCHES
    
    if matches_played >= max_matches:
        await update.message.reply_text("Hai raggiunto il numero massimo di partite disponibili. Diventa VIP per giocare di più!")
        return
    
    score = f"{random.randint(0,5)}-{random.randint(0,5)}"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO matches_history (user_id, score) VALUES (?, ?)", (user_id, score))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"Partita giocata! Punteggio: {score}")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT u.username, SUM(CAST(SUBSTR(m.score, 1, INSTR(m.score, '-')-1) AS INTEGER)) AS total_goals
        FROM matches_history m
        JOIN users u ON u.user_id = m.user_id
        GROUP BY u.username
        ORDER BY total_goals DESC
        LIMIT 10
    """)
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        await update.message.reply_text("Nessuna partita giocata finora.")
        return
    
    msg = "🏆 Top 10 giocatori (gol fatti totali):\n"
    for i, (username, total_goals) in enumerate(rows, start=1):
        msg += f"{i}. {username} → {total_goals} gol\n"
    await update.message.reply_text(msg)

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT score FROM matches_history WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        await update.message.reply_text("Non hai ancora giocato partite.")
        return
    
    msg = "📄 Le tue partite:\n"
    for i, (score,) in enumerate(rows, start=1):
        msg += f"{i}. {score}\n"
    await update.message.reply_text(msg)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    if not TG_BOT_TOKEN:
        raise ValueError("TG_BOT_TOKEN non è impostato")
    
    init_db()
    
    application = ApplicationBuilder().token(TG_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("match", match))
    application.add_handler(CommandHandler("leaderboard", leaderboard))
    application.add_handler(CommandHandler("history", history))
    
    application.run_polling()
