import json
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.configurazione import nomi_barche_configurate
from app.database import ottieni_db
from app.modelli.prenotazione import Prenotazione
from app.modelli.risorsa import Risorsa

router = APIRouter(tags=["Barche"])


class RisorsaOutput(BaseModel):
    id: int
    nome: str
    tipologia: str | None
    descrizione: str | None

    model_config = {"from_attributes": True}


class RisorsaStatoOutput(BaseModel):
    id: int
    nome: str
    tipologia: str | None
    descrizione: str | None
    occupata: bool
    id_prenotazione_attiva: int | None
    organizzatore: str | None
    data_prenotazione: datetime | None
    ora_partenza_effettiva: datetime | None
    ora_partenza: datetime | None
    ora_rientro_prevista: datetime | None
    ora_rientro_effettiva: datetime | None
    nota: str | None
    persone_imbarcate: list[str]


@router.get(
    "/risorse",
    response_model=list[RisorsaOutput],
    summary="Elenca le barche",
    description="Restituisce l'elenco completo delle barche disponibili nel circolo.",
    responses={200: {"description": "Risposta completata"}},
)
def elenco_risorse(db: Session = Depends(ottieni_db)):
    nomi_configurati = nomi_barche_configurate()
    if not nomi_configurati:
        return []
    return db.query(Risorsa).filter(Risorsa.nome.in_(nomi_configurati)).order_by(Risorsa.nome).all()


@router.get(
    "/risorse/tipologie",
    response_model=list[str],
    summary="Elenca le tipologie di barca",
    description="Restituisce le tipologie disponibili per filtrare le barche.",
    responses={200: {"description": "Risposta completata"}},
)
def elenco_tipologie_risorse(db: Session = Depends(ottieni_db)):
    tipologie = (
        db.query(Risorsa.tipologia)
        .filter(Risorsa.tipologia.is_not(None))
        .distinct()
        .order_by(Risorsa.tipologia)
        .all()
    )
    return [tipologia for (tipologia,) in tipologie]


@router.get(
    "/risorse/stato",
    response_model=list[RisorsaStatoOutput],
    summary="Elenca le barche con il loro stato",
    description="Mostra per ogni barca se e libera o occupata e da chi.",
    responses={200: {"description": "Risposta completata"}},
)
def elenco_risorse_con_stato(
    tipologia: str | None = None,
    db: Session = Depends(ottieni_db),
):
    nomi_configurati = nomi_barche_configurate(tipologia)
    if not nomi_configurati:
        return []
    query = db.query(Risorsa).filter(Risorsa.nome.in_(nomi_configurati))
    if tipologia:
        query = query.filter(Risorsa.tipologia == tipologia)
    risorse = query.order_by(Risorsa.nome).all()

    risultato: list[RisorsaStatoOutput] = []
    for risorsa in risorse:
        prenotazione_attiva = (
            db.query(Prenotazione)
            .filter(
                Prenotazione.id_risorsa == risorsa.id,
                Prenotazione.chiusa.is_(False),
            )
            .order_by(Prenotazione.inizio.desc())
            .first()
        )
        organizzatore = None
        if prenotazione_attiva is not None:
            organizzatore = f"{prenotazione_attiva.creatore.nome} {prenotazione_attiva.creatore.cognome or ''}".strip()

        risultato.append(
            RisorsaStatoOutput(
                id=risorsa.id,
                nome=risorsa.nome,
                tipologia=risorsa.tipologia,
                descrizione=risorsa.descrizione,
                occupata=prenotazione_attiva is not None,
                id_prenotazione_attiva=prenotazione_attiva.id if prenotazione_attiva else None,
                organizzatore=organizzatore,
                data_prenotazione=prenotazione_attiva.inizio if prenotazione_attiva else None,
                ora_partenza_effettiva=prenotazione_attiva.ora_partenza_effettiva if prenotazione_attiva else None,
                ora_partenza=prenotazione_attiva.inizio if prenotazione_attiva else None,
                ora_rientro_prevista=prenotazione_attiva.fine if prenotazione_attiva else None,
                ora_rientro_effettiva=prenotazione_attiva.ora_rientro_effettiva if prenotazione_attiva else None,
                nota=prenotazione_attiva.nota if prenotazione_attiva else None,
                persone_imbarcate=(
                    json.loads(prenotazione_attiva.persone_imbarcate)
                    if prenotazione_attiva and prenotazione_attiva.persone_imbarcate
                    else []
                ),
            )
        )
    return risultato


@router.get(
    "/risorse/disponibili",
    response_model=list[RisorsaOutput],
    summary="Elenca le barche libere",
    description="Mostra le barche non occupate nell'intervallo richiesto.",
    responses={200: {"description": "Risposta completata"}},
)
def elenco_risorse_disponibili(
    inizio: datetime,
    fine: datetime,
    tipologia: str | None = None,
    db: Session = Depends(ottieni_db),
):
    prenotazioni_in_conflitto = (
        select(Prenotazione.id_risorsa)
        .filter(Prenotazione.chiusa.is_(False))
    )
    nomi_configurati = nomi_barche_configurate(tipologia)
    if not nomi_configurati:
        return []
    query = db.query(Risorsa).filter(
        Risorsa.nome.in_(nomi_configurati),
        ~Risorsa.id.in_(prenotazioni_in_conflitto),
    )
    if tipologia:
        query = query.filter(Risorsa.tipologia == tipologia)
    return query.order_by(Risorsa.nome).all()
