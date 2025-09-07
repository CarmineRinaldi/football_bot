def handle_callback(callback_data, update, context):
    user_id = update["callback_query"]["from"]["id"]

    # Menu principale
    if callback_data == "main_menu":
        return show_main_menu(update, context)

    # Selezione piano
    if callback_data.startswith("plan_"):
        plan = callback_data.split("_")[1]
        return show_plan_info(update, context, plan)

    # Campionati paginati
    if callback_data.startswith("select_league_"):
        plan = callback_data.split("_")[-1]
        return show_leagues(update, context, plan)

    # Nazionali paginati
    if callback_data.startswith("select_national_"):
        plan = callback_data.split("_")[-1]
        return show_nationals(update, context, plan)

    # Pagine campionati/nazionali
    if "_page_" in callback_data:
        parts = callback_data.split("_")
        prefix = parts[0]  # 'league' o 'national'
        try:
            page = int(parts[2])
        except ValueError:
            page = 0  # fallback se non riesce a convertire
        plan = parts[3]
        if prefix == "league":
            return show_leagues(update, context, plan, page)
        else:
            return show_nationals(update, context, plan, page)

    # Risultati ricerca
    if callback_data.startswith("search_"):
        parts = callback_data.split("_")
        if parts[0] == "search" and parts[1] != "result":
            plan = parts[1]
            return {"text": "Scrivi il nome della squadra o del campionato da cercare:"}
        elif parts[1] == "result":
            try:
                league_id = int(parts[2])
            except ValueError:
                return {"text": "⚠️ ID campionato non valido!"}
            plan = parts[3]
            return show_matches(update, context, league_id, plan)

    # Selezione partita
    if callback_data.startswith("match_"):
        match_id = callback_data.split("_")[1]
        # Qui puoi aggiungere logica per salvare il match selezionato
        return {"text": f"✅ Hai selezionato la partita {match_id}!"}

    # Fallback se il callback non è riconosciuto
    return {"text": "⚠️ Comando non riconosciuto.", "reply_markup": {"inline_keyboard": [[{"text": "🔙 Indietro", "callback_data": "main_menu"}]]}}
