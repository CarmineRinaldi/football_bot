from __future__ import annotations
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from .config import settings
from . import database
from . import keyboards as kb
from .utils import wipe_and_send, format_slip, combined_odds
from .api_football import TOP_LEAGUES, get_fixtures, get_odds_1x2
from .stripe_utils import create_checkout_session

bot = Bot(token=settings.TG_BOT_TOKEN, parse_mode="HTML")
router = Router()
dp = Dispatcher()
dp.include_router(router)

# --- Helpers ---
async def ensure_user(msg: Message | CallbackQuery) -> int:
    user = msg.from_user
    await database.upsert_user(user.id, user.username, user.first_name)
    await database.ensure_free_if_expired(user.id)
    return user.id

# --- Commands ---
@router.message(CommandStart())
async def on_start(msg: Message):
    await ensure_user(msg)
    text = (
        "<b>Benvenuto!</b>\n\n"
        "Questo bot crea <b>schedine calcio con quote reali</b>.\n"
        "Piani: Free, Pack 2€ (10 schedine), VIP 4,99€/mese.\n\n"
        "Scegli dal menu qui sotto."
    )
    await wipe_and_send(bot, None, msg.chat.id, text, reply_markup=kb.main_menu_kb())

# --- Menu navigation ---
@router.callback_query(F.data.startswith("menu:"))
async def on_menu(cq: CallbackQuery):
    uid = await ensure_user(cq)
    parts = cq.data.split(":")
    action = parts[1]
    if action == "main":
        await wipe_and_send(bot, cq, cq.message.chat.id, "🏠 Menù principale", reply_markup=kb.main_menu_kb())
    elif action == "leagues":
        page = int(parts[2]) if len(parts) > 2 else 0
        await wipe_and_send(bot, cq, cq.message.chat.id, "🏆 Seleziona campionato",
                            reply_markup=kb.leagues_kb(TOP_LEAGUES, page))
    elif action == "plans":
        await wipe_and_send(bot, cq, cq.message.chat.id, "💳 Piani & Prezzi", reply_markup=kb.plans_kb())
    elif action == "my_slips":
        rows = await database.list_slips(uid)
        if not rows:
            await wipe_and_send(bot, cq, cq.message.chat.id, "🧾 Non hai schedine salvate negli ultimi 10 giorni.",
                                reply_markup=kb.back_to_main_kb())
        else:
            lines = []
            for r in rows:
                items = r["items_json"]
                lines.append(f"ID {r['id']} — quota {r['combined_odds']} — exp <code>{r['expires_at']}</code>")
            await wipe_and_send(bot, cq, cq.message.chat.id, "🧾 Le mie schedine:\n\n" + "\n".join(lines),
                                reply_markup=kb.back_to_main_kb())
    elif action == "account":
        u = await database.get_user(uid)
        plan = u["plan"]
        vip_until = u["vip_until"]
        credits = u["slip_credits"]
        txt = (f"👤 <b>Account</b>\n\n"
               f"• Piano: <b>{plan.upper()}</b>\n"
               f"• VIP fino a: <code>{vip_until}</code>\n"
               f"• Crediti schedine: <b>{credits}</b>")
        await wipe_and_send(bot, cq, cq.message.chat.id, txt, reply_markup=kb.back_to_main_kb())

# --- Leagues → Fixtures ---
@router.callback_query(F.data.startswith("league:"))
async def on_league(cq: CallbackQuery):
    parts = cq.data.split(":")
    league_id = int(parts[1])
    page = int(parts[3]) if len(parts) > 3 else 0
    fixtures = await get_fixtures(league_id)
    if not fixtures:
        await wipe_and_send(bot, cq, cq.message.chat.id, "Nessuna partita trovata.", reply_markup=kb.back_to_main_kb())
        return
    await wipe_and_send(bot, cq, cq.message.chat.id, f"📅 Partite — League {league_id}",
                        reply_markup=kb.fixtures_kb(fixtures, league_id, page))

# --- Fixture → Markets ---
@router.callback_query(F.data.startswith("fixture:"))
async def on_fixture_markets(cq: CallbackQuery):
    fixture_id = int(cq.data.split(":")[1])
    await wipe_and_send(bot, cq, cq.message.chat.id, f"📊 Mercati per fixture <code>{fixture_id}</code>",
                        reply_markup=kb.markets_kb(fixture_id))

# --- Markets: 1x2 odds ---
@router.callback_query(F.data.startswith("market:"))
async def on_market(cq: CallbackQuery):
    parts = cq.data.split(":")
    fixture_id = int(parts[1])
    market = parts[2]
    if market != "1x2":
        await wipe_and_send(bot, cq, cq.message.chat.id, "Per ora è attivo solo 1X2.", reply_markup=kb.back_to_main_kb())
        return
    odds, home, away = await get_odds_1x2(fixture_id)
    if not odds:
        await wipe_and_send(bot, cq, cq.message.chat.id, "Quote non disponibili per questo match.",
                            reply_markup=kb.back_to_main_kb())
        return
    title = f"⚔️ {home} vs {away}\nScegli l'esito 1X2:"
    await wipe_and_send(bot, cq, cq.message.chat.id, title, reply_markup=kb.picks_1x2_kb(fixture_id, odds))

# --- Pick (aggiunge al draft) ---
@router.callback_query(F.data.startswith("pick:"))
async def on_pick(cq: CallbackQuery):
    uid = await ensure_user(cq)
    _, fixture_id, market, pick = cq.data.split(":")
    fixture_id = int(fixture_id)
    odds, home, away = await get_odds_1x2(fixture_id)
    odd = odds.get(pick)
    if not odd:
        await wipe_and_send(bot, cq, cq.message.chat.id, "Quota non disponibile.", reply_markup=kb.back_to_main_kb())
        return

    draft = await database.get_or_create_draft(uid)
    items = draft["items"]
    # Limiti per piano
    u = await database.get_user(uid)
    max_matches = settings.VIP_MAX_MATCHES if u["plan"] == "vip" else settings.FREE_MAX_MATCHES
    if len(items) >= max_matches:
        await wipe_and_send(bot, cq, cq.message.chat.id,
                            f"Limite raggiunto ({max_matches} selezioni). Rimuovi qualcosa o salva la schedina.",
                            reply_markup=kb.back_to_main_kb())
        return

    # Evita duplicati stesso fixture
    items = [it for it in items if int(it.get("fixture_id")) != fixture_id]
    items.append({
        "fixture_id": fixture_id,
        "league_id": 0,
        "home": home,
        "away": away,
        "market": "1x2",
        "pick": pick,
        "odd": float(odd),
    })
    await database.save_draft(uid, items)

    txt = "✅ Aggiunta selezione:\n\n" + format_slip(items)
    await wipe_and_send(bot, cq, cq.message.chat.id, txt, reply_markup=kb.slip_actions_kb(can_save=True))

# --- Slip view/clear/save ---
@router.callback_query(F.data == "slip:view")
async def on_slip_view(cq: CallbackQuery):
    uid = await ensure_user(cq)
    draft = await database.get_or_create_draft(uid)
    items = draft["items"]
    txt = format_slip(items)
    can_save = len(items) > 0
    await wipe_and_send(bot, cq, cq.message.chat.id, txt, reply_markup=kb.slip_actions_kb(can_save))

@router.callback_query(F.data == "slip:clear")
async def on_slip_clear(cq: CallbackQuery):
    uid = await ensure_user(cq)
    await database.clear_draft(uid)
    await wipe_and_send(bot, cq, cq.message.chat.id, "🧹 Schedina svuotata.", reply_markup=kb.back_to_main_kb())

@router.callback_query(F.data == "slip:save")
async def on_slip_save(cq: CallbackQuery):
    uid = await ensure_user(cq)
    draft = await database.get_or_create_draft(uid)
    items = draft["items"]
    if not items:
        await wipe_and_send(bot, cq, cq.message.chat.id, "La schedina è vuota.", reply_markup=kb.back_to_main_kb())
        return
    # Serve VIP o credito
    ok = await database.consume_credit_if_needed(uid)
    if not ok:
        await wipe_and_send(bot, cq, cq.message.chat.id,
                            "❌ Non hai crediti. Compra il pack 10 schedine (2€) o attiva il VIP.",
                            reply_markup=kb.plans_kb())
        return
    co = combined_odds(items)
    slip_id = await database.insert_slip(uid, items, co)
    await database.clear_draft(uid)
    await wipe_and_send(bot, cq, cq.message.chat.id,
                        f"💾 Schedina salvata (ID {slip_id}). Quota totale: <b>{co}</b>",
                        reply_markup=kb.back_to_main_kb())

# --- Piani acquisto (Stripe) ---
@router.callback_query(F.data.startswith("buy:"))
async def on_buy(cq: CallbackQuery):
    uid = await ensure_user(cq)
    kind = cq.data.split(":")[1]  # "pack" | "vip"
    try:
        url = await create_checkout_session(uid, kind)
        if kind == "pack":
            txt = "🎟️ Pack 10 schedine — 2€\nPaga in sicurezza con Stripe:"
        else:
            txt = "⭐ VIP — 4,99€/mese\nAbbonati con Stripe:"
        await wipe_and_send(bot, cq, cq.message.chat.id, f"{txt}\n{url}", reply_markup=kb.back_to_main_kb())
    except Exception as e:
        await wipe_and_send(bot, cq, cq.message.chat.id, f"Errore Stripe: {e}", reply_markup=kb.back_to_main_kb())
