import json
import os
from pathlib import Path
from typing import Any


PERCORSO_BASE = Path(__file__).resolve().parent.parent


CONFIGURAZIONE_APP: dict[str, Any] = {
    "nome_app": os.getenv("NOME_APP", "Prenotazioni Imbarcazioni"),
    "nome_breve": os.getenv("NOME_BREVE_APP", "Prenotazioni"),
    "descrizione_api": "API per registrazione utenti, gestione imbarcazioni e registro uscite.",
    "logo": {
        "riga_1": os.getenv("LOGO_RIGA_1", "PRENOTAZIONI"),
        "riga_2": os.getenv("LOGO_RIGA_2", "IMBARCAZIONI"),
        "riga_3": os.getenv("LOGO_RIGA_3", "APP"),
    },
    "home": {
        "eyebrow": "Gestionale nautico personalizzabile",
        "titolo": "Registro uscite",
        "sottotitolo": (
            "Una base pronta per circoli, scuole vela e associazioni nautiche, "
            "personalizzabile con nome, colori, contatti, regolamento e flotta."
        ),
        "testo": (
            "Il socio sceglie l'imbarcazione, registra l'uscita e conferma il rientro. "
            "Lo storico resta salvato nel registro uscite e le imbarcazioni tornano "
            "disponibili appena l'uscita viene chiusa."
        ),
    },
    "etichette": {
        "persona": "socio",
        "tessera": "Numero tessera",
        "quota_annuale": "Il socio e in regola con la quota annuale",
        "certificato_medico": "Il certificato medico e stato consegnato",
    },
    "contatti": {
        "titolo_telefono": "Segreteria",
        "telefono_label": "Telefono",
        "telefono": os.getenv("TELEFONO_CIRCOLO", "+390000000000"),
        "telefono_visibile": os.getenv("TELEFONO_VISIBILE", "000 0000000"),
        "email": os.getenv("EMAIL_CIRCOLO", "info@example.com"),
        "luogo": os.getenv("LUOGO_CIRCOLO", "Sede da personalizzare"),
        "citta": os.getenv("CITTA_CIRCOLO", "Citta da personalizzare"),
    },
    "orari": {
        "titolo": "Orari",
        "sede_titolo": "Orari sede",
        "servizio_titolo": "Orari servizio",
        "feriali": {
            "giorni": "Lunedi - Venerdi",
            "apertura": "08:45",
            "chiusura": "19:00",
        },
        "festivi": {
            "giorni": "Sabato, Domenica",
            "apertura": "08:15",
            "chiusura": "19:30",
        },
    },
    "database_nome": os.getenv("NOME_DATABASE", "app_gestionale_vela.db"),
    "dominio_email_interna": os.getenv("DOMINIO_EMAIL_INTERNA", "app.local"),
    "codice_amministratore": os.getenv("CODICE_AMMINISTRATORE", "admin"),
    "percorso_regolamento": os.getenv(
        "PERCORSO_REGOLAMENTO",
        str(PERCORSO_BASE / "documenti" / "regolamento.pdf"),
    ),
    "percorso_upload": os.getenv("PERCORSO_UPLOAD", str(PERCORSO_BASE / "uploads")),
    "categorie_barche": [
        {
            "codice": "derive",
            "etichetta": "Derive",
            "barche": [f"Deriva {numero}" for numero in range(1, 8)],
        },
        {
            "codice": "laser",
            "etichetta": "Laser",
            "barche": [f"Laser {numero}" for numero in range(1, 8)],
        },
        {
            "codice": "topaz",
            "etichetta": "Topaz",
            "barche": ["Topaz 1", "Topaz 2"],
        },
        {
            "codice": "dinghy",
            "etichetta": "Dinghy",
            "barche": ["Dinghy 1", "Dinghy 2"],
        },
        {
            "codice": "catamarani",
            "etichetta": "Catamarani",
            "barche": ["Catamarano 1"],
        },
        {
            "codice": "altura",
            "etichetta": "Altura",
            "barche": ["Altura 1"],
        },
        {
            "codice": "imbarcazioni_appoggio",
            "etichetta": "Imbarcazioni d'appoggio",
            "barche": ["Gommone 1", "Gommone 2", "Gommone 3", "Gommone 4"],
        },
    ],
}


def aggiorna_configurazione(base: dict[str, Any], personalizzata: dict[str, Any]) -> dict[str, Any]:
    for chiave, valore in personalizzata.items():
        if isinstance(valore, dict) and isinstance(base.get(chiave), dict):
            aggiorna_configurazione(base[chiave], valore)
        else:
            base[chiave] = valore
    return base


def normalizza_codice(testo: str) -> str:
    pulito = "".join(carattere.lower() if carattere.isalnum() else "_" for carattere in testo)
    while "__" in pulito:
        pulito = pulito.replace("__", "_")
    return pulito.strip("_") or "categoria"


def normalizza_categorie(categorie: list[dict[str, Any]]) -> list[dict[str, Any]]:
    categorie_normalizzate: list[dict[str, Any]] = []
    codici_usati: set[str] = set()
    for indice, categoria in enumerate(categorie, start=1):
        etichetta = str(categoria.get("etichetta") or categoria.get("codice") or f"Categoria {indice}").strip()
        codice_base = str(categoria.get("codice") or normalizza_codice(etichetta)).strip()
        codice = normalizza_codice(codice_base)
        while codice in codici_usati:
            codice = f"{codice}_{indice}"
        codici_usati.add(codice)

        barche_raw = categoria.get("barche") or []
        barche = []
        for nome_barca in barche_raw:
            nome = str(nome_barca).strip()
            if nome and nome not in barche:
                barche.append(nome)
        if not barche:
            continue
        categorie_normalizzate.append(
            {
                "codice": codice,
                "etichetta": etichetta,
                "barche": barche,
            }
        )
    return categorie_normalizzate


CONFIGURAZIONE_APP["categorie_barche"] = normalizza_categorie(CONFIGURAZIONE_APP["categorie_barche"])


PERCORSO_CONFIG_CLIENTE = PERCORSO_BASE / "configurazione_cliente.json"
if PERCORSO_CONFIG_CLIENTE.exists():
    with PERCORSO_CONFIG_CLIENTE.open("r", encoding="utf-8") as file_config:
        aggiorna_configurazione(CONFIGURAZIONE_APP, json.load(file_config))
    CONFIGURAZIONE_APP["categorie_barche"] = normalizza_categorie(CONFIGURAZIONE_APP["categorie_barche"])


def salva_configurazione_cliente(nuova_configurazione: dict[str, Any]) -> None:
    aggiorna_configurazione(CONFIGURAZIONE_APP, nuova_configurazione)
    CONFIGURAZIONE_APP["categorie_barche"] = normalizza_categorie(CONFIGURAZIONE_APP["categorie_barche"])
    PERCORSO_CONFIG_CLIENTE.write_text(
        json.dumps(CONFIGURAZIONE_APP, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def percorso_database() -> Path:
    return PERCORSO_BASE / str(CONFIGURAZIONE_APP["database_nome"])


def percorso_upload() -> Path:
    return Path(str(CONFIGURAZIONE_APP["percorso_upload"]))


def percorso_regolamento() -> Path:
    return Path(str(CONFIGURAZIONE_APP["percorso_regolamento"]))


def codice_amministratore() -> str:
    return str(CONFIGURAZIONE_APP["codice_amministratore"])


def elenco_barche_configurate() -> list[tuple[str, str]]:
    barche: list[tuple[str, str]] = []
    for categoria in CONFIGURAZIONE_APP["categorie_barche"]:
        codice = str(categoria["codice"])
        for nome in categoria["barche"]:
            barche.append((str(nome), codice))
    return barche


def categorie_barche_configurate() -> list[dict[str, Any]]:
    return list(CONFIGURAZIONE_APP["categorie_barche"])


def nomi_barche_configurate(tipologia: str | None = None) -> list[str]:
    nomi: list[str] = []
    for categoria in CONFIGURAZIONE_APP["categorie_barche"]:
        if tipologia is not None and categoria["codice"] != tipologia:
            continue
        nomi.extend(str(nome) for nome in categoria["barche"])
    return nomi


def configurazione_frontend_json() -> str:
    categorie = CONFIGURAZIONE_APP["categorie_barche"]
    payload = {
        "nome_app": CONFIGURAZIONE_APP["nome_app"],
        "nome_breve": CONFIGURAZIONE_APP["nome_breve"],
        "logo": CONFIGURAZIONE_APP["logo"],
        "home": CONFIGURAZIONE_APP["home"],
        "contatti": CONFIGURAZIONE_APP["contatti"],
        "orari": CONFIGURAZIONE_APP["orari"],
        "etichette": CONFIGURAZIONE_APP["etichette"],
        "tipologie": [categoria["codice"] for categoria in categorie],
        "etichette_tipologie": {
            categoria["codice"]: categoria["etichetta"] for categoria in categorie
        },
        "chiave_socio": "gestionale-vela-socio",
        "chiave_uscite_notificate": "gestionale-vela-uscite-notificate",
    }
    return json.dumps(payload, ensure_ascii=False)
