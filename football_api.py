import random
from database import add_schedina

CAMPIONATI = [
    "Serie A", "Serie B", "Premier League", "La Liga",
    "Bundesliga", "Ligue 1", "Champions League", "Europa League"
]

PARTITE_SIMULATE = {
    "Serie A": [
        ("Juventus", "Inter", 1.8, 3.4, 4.2),
        ("Milan", "Napoli", 2.0, 3.3, 3.5),
        ("Roma", "Lazio", 2.1, 3.2, 3.6),
        ("Atalanta", "Fiorentina", 1.9, 3.3, 4.0),
        ("Sassuolo", "Torino", 2.3, 3.1, 3.2)
    ],
    "Serie B": [
        ("Brescia", "Frosinone", 2.0, 3.3, 3.5),
        ("Parma", "Benevento", 2.1, 3.2, 3.4),
        ("Cremonese", "Ascoli", 2.2, 3.1, 3.3),
        ("SPAL", "Modena", 2.0, 3.3, 3.6),
        ("Reggina", "Cosenza", 1.9, 3.4, 4.0)
    ]
}

def get_campionati():
    return CAMPIONATI

def genera_schedine_free(user_id, campionato):
    if campionato not in PARTITE_SIMULATE:
        return ["Nessuna schedina disponibile per questo campionato."]
    partite = PARTITE_SIMULATE[campionato]
    schedine_testo = []
    for i in range(5):
        n_partite = random.randint(2, min(4, len(partite)))
        selezione = random.sample(partite, n_partite)
        pronostico = []
        for home, away, q1, qx, q2 in selezione:
            scelta = random.choices(["1", "X", "2"], weights=[q2, qx, q1], k=1)[0]
            pronostico.append(f"{home} vs {away}: {scelta}")
        testo_schedina = "\n".join(pronostico)
        schedine_testo.append(testo_schedina)
        add_schedina(user_id, campionato, testo_schedina)
    return schedine_testo

def get_pronostico(user_id, campionato):
    schedine = genera_schedine_free(user_id, campionato)
    return "\n\n".join([f"Schedina {i+1}:\n{s}" for i, s in enumerate(schedine)])
