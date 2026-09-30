import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.configurazione import percorso_upload
from app.database import ottieni_db
from app.modelli.prenotazione import Prenotazione
from app.modelli.risorsa import Risorsa
from app.modelli.utente import RuoloUtente, Utente
from app.rotte.utenti import utente_idoneo

router = APIRouter(tags=["Prenotazioni"])
PERCORSO_FOTO_DANNI = percorso_upload() / "danni"


class CreazionePrenotazione(BaseModel):
    id_creatore: int = Field(..., description="ID della persona che inserisce la prenotazione")
    id_risorsa: int = Field(..., description="ID della barca da prenotare")
    inizio: datetime = Field(..., description="Data e ora di uscita")
    fine: datetime = Field(..., description="Data e ora di rientro")
    persone_imbarcate: list[str] = Field(
        default_factory=list,
        description="Elenco delle persone che parteciperanno all'uscita",
    )
    nota: str | None = Field(
        default=None,
        description="Note generali sull'uscita o richieste di partecipazione",
    )
    danni: str | None = Field(
        default=None,
        description="Eventuali danni riscontrati al rientro",
    )
    aperta_al_circolo: bool = Field(
        default=False,
        description="Indica se l'uscita viene messa a disposizione del circolo",
    )


class PrenotazioneOutput(BaseModel):
    id: int
    id_creatore: int
    id_risorsa: int
    inizio: datetime
    fine: datetime
    ora_partenza_effettiva: datetime | None
    ora_rientro_effettiva: datetime | None
    persone_imbarcate: list[str]
    nota: str | None
    nota_rientro: str | None
    danni: str | None
    foto_danni: list[str]
    aperta_al_circolo: bool
    chiusa: bool


class PrenotazioneDisponibileOutput(BaseModel):
    id: int
    barca: str
    organizzatore: str
    ruolo_organizzatore: RuoloUtente
    inizio: datetime
    fine: datetime
    nota: str | None
    persone_imbarcate: list[str]
    contatto_email: str
    contatto_telefono: str | None


class ChiusuraPrenotazione(BaseModel):
    ora_partenza_effettiva: datetime = Field(..., description="Ora effettiva di partenza")
    ora_rientro_effettiva: datetime = Field(..., description="Ora effettiva di rientro")
    persone_imbarcate: list[str] = Field(
        default_factory=list,
        description="Elenco aggiornato dell'equipaggio effettivamente imbarcato",
    )
    nota_rientro: str | None = Field(
        default=None,
        description="Nota finale sullo stato dell'imbarcazione al rientro",
    )
    danni: str | None = Field(
        default=None,
        description="Eventuali danni rilevati al rientro",
    )
    foto_danni: list[str] = Field(
        default_factory=list,
        description="Percorsi delle foto caricate per documentare eventuali danni",
    )


class PrenotazioneAttivaOutput(BaseModel):
    id: int
    id_risorsa: int
    barca: str
    organizzatore: str
    inizio: datetime
    fine: datetime
    nota: str | None
    aperta_al_circolo: bool


class RegistroUscitaOutput(BaseModel):
    id: int
    barca: str
    tipologia: str | None
    organizzatore: str
    data_uscita: str
    ora_partenza: datetime | None
    ora_arrivo: datetime | None
    nota: str | None
    nota_rientro: str | None
    danni: str | None
    foto_danni: list[str]
    persone_imbarcate: list[str]
    chiusa: bool


def decodifica_persone_imbarcate(prenotazione: Prenotazione) -> list[str]:
    if not prenotazione.persone_imbarcate:
        return []
    return json.loads(prenotazione.persone_imbarcate)


def decodifica_foto_danni(prenotazione: Prenotazione) -> list[str]:
    if not prenotazione.foto_danni:
        return []
    return json.loads(prenotazione.foto_danni)


def nome_completo_utente(utente: Utente) -> str:
    return f"{utente.nome} {utente.cognome or ''}".strip()


def prenotazione_in_conflitto(
    db: Session,
    id_risorsa: int,
    inizio: datetime,
    fine: datetime,
) -> bool:
    return (
        db.query(Prenotazione)
        .filter(
            Prenotazione.id_risorsa == id_risorsa,
            Prenotazione.chiusa.is_(False),
        )
        .first()
        is not None
    )


@router.post(
    "/prenotazioni",
    response_model=PrenotazioneOutput,
    status_code=status.HTTP_201_CREATED,
    summary="Crea una prenotazione",
    description="Prenota una barca, indica gli orari, chi esce e le note dell'uscita.",
    responses={
        201: {"description": "Prenotazione creata con successo"},
        400: {"description": "Richiesta non valida"},
        404: {"description": "Barca o utente non trovato"},
        422: {"description": "Errore di validazione"},
    },
)
def crea_prenotazione(payload: CreazionePrenotazione, db: Session = Depends(ottieni_db)):
    utente = db.query(Utente).filter(Utente.id == payload.id_creatore).first()
    if utente is None:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    if not utente_idoneo(utente):
        raise HTTPException(
            status_code=400,
            detail="Il socio deve essere sbloccato dall'amministratore per l'anno corrente",
        )

    risorsa = db.query(Risorsa).filter(Risorsa.id == payload.id_risorsa).first()
    if risorsa is None:
        raise HTTPException(status_code=404, detail="Barca non trovata")

    if payload.fine <= payload.inizio:
        raise HTTPException(
            status_code=400,
            detail="L'orario di rientro deve essere successivo a quello di uscita",
        )

    if prenotazione_in_conflitto(db, payload.id_risorsa, payload.inizio, payload.fine):
        raise HTTPException(
            status_code=400,
            detail="La barca selezionata e gia occupata in questo intervallo",
        )

    prenotazione = Prenotazione(
        id_creatore=payload.id_creatore,
        id_risorsa=payload.id_risorsa,
        inizio=payload.inizio,
        fine=payload.fine,
        persone_imbarcate=json.dumps(payload.persone_imbarcate, ensure_ascii=False),
        nota=payload.nota,
        danni=payload.danni,
        foto_danni=json.dumps([], ensure_ascii=False),
        aperta_al_circolo=payload.aperta_al_circolo,
    )
    utente.disponibile_per_circolo = payload.aperta_al_circolo
    utente.nota_disponibilita = payload.nota if payload.aperta_al_circolo else None
    db.add(prenotazione)
    db.commit()
    db.refresh(prenotazione)
    return PrenotazioneOutput(
        id=prenotazione.id,
        id_creatore=prenotazione.id_creatore,
        id_risorsa=prenotazione.id_risorsa,
        inizio=prenotazione.inizio,
        fine=prenotazione.fine,
        ora_rientro_effettiva=prenotazione.ora_rientro_effettiva,
        ora_partenza_effettiva=prenotazione.ora_partenza_effettiva,
        persone_imbarcate=decodifica_persone_imbarcate(prenotazione),
        nota=prenotazione.nota,
        nota_rientro=prenotazione.nota_rientro,
        danni=prenotazione.danni,
        foto_danni=decodifica_foto_danni(prenotazione),
        aperta_al_circolo=prenotazione.aperta_al_circolo,
        chiusa=prenotazione.chiusa,
    )


@router.get(
    "/prenotazioni/attive",
    response_model=list[PrenotazioneAttivaOutput],
    summary="Elenca le prenotazioni attive",
    description="Mostra le uscite ancora aperte, quindi le barche attualmente occupate.",
    responses={200: {"description": "Risposta completata"}},
)
def elenco_prenotazioni_attive(db: Session = Depends(ottieni_db)):
    prenotazioni = (
        db.query(Prenotazione)
        .join(Utente, Prenotazione.id_creatore == Utente.id)
        .join(Risorsa, Prenotazione.id_risorsa == Risorsa.id)
        .filter(Prenotazione.chiusa.is_(False))
        .order_by(Prenotazione.inizio.desc())
        .all()
    )
    return [
        PrenotazioneAttivaOutput(
            id=prenotazione.id,
            id_risorsa=prenotazione.id_risorsa,
            barca=prenotazione.risorsa.nome,
            organizzatore=nome_completo_utente(prenotazione.creatore),
            inizio=prenotazione.inizio,
            fine=prenotazione.fine,
            nota=prenotazione.nota,
            aperta_al_circolo=prenotazione.aperta_al_circolo,
        )
        for prenotazione in prenotazioni
    ]


@router.put(
    "/prenotazioni/{id_prenotazione}/chiusura",
    response_model=PrenotazioneOutput,
    summary="Chiude una prenotazione",
    description="Registra il rientro effettivo, la nota finale e rende di nuovo disponibile la barca.",
    responses={
        200: {"description": "Prenotazione chiusa correttamente"},
        404: {"description": "Prenotazione non trovata"},
        400: {"description": "Richiesta non valida"},
    },
)
def chiudi_prenotazione(
    id_prenotazione: int,
    payload: ChiusuraPrenotazione,
    db: Session = Depends(ottieni_db),
):
    prenotazione = db.query(Prenotazione).filter(Prenotazione.id == id_prenotazione).first()
    if prenotazione is None:
        raise HTTPException(status_code=404, detail="Prenotazione non trovata")

    if prenotazione.chiusa:
        raise HTTPException(status_code=400, detail="Questa prenotazione e gia stata chiusa")

    if payload.ora_rientro_effettiva < payload.ora_partenza_effettiva:
        raise HTTPException(
            status_code=400,
            detail="L'ora di arrivo non puo essere precedente all'ora di partenza",
        )

    prenotazione.ora_partenza_effettiva = payload.ora_partenza_effettiva
    prenotazione.ora_rientro_effettiva = payload.ora_rientro_effettiva
    prenotazione.persone_imbarcate = json.dumps(payload.persone_imbarcate, ensure_ascii=False)
    prenotazione.nota_rientro = payload.nota_rientro
    prenotazione.danni = payload.danni
    prenotazione.foto_danni = json.dumps(payload.foto_danni, ensure_ascii=False)
    prenotazione.chiusa = True
    prenotazione.creatore.disponibile_per_circolo = False
    prenotazione.creatore.nota_disponibilita = None
    db.commit()
    db.refresh(prenotazione)

    return PrenotazioneOutput(
        id=prenotazione.id,
        id_creatore=prenotazione.id_creatore,
        id_risorsa=prenotazione.id_risorsa,
        inizio=prenotazione.inizio,
        fine=prenotazione.fine,
        ora_partenza_effettiva=prenotazione.ora_partenza_effettiva,
        ora_rientro_effettiva=prenotazione.ora_rientro_effettiva,
        persone_imbarcate=decodifica_persone_imbarcate(prenotazione),
        nota=prenotazione.nota,
        nota_rientro=prenotazione.nota_rientro,
        danni=prenotazione.danni,
        foto_danni=decodifica_foto_danni(prenotazione),
        aperta_al_circolo=prenotazione.aperta_al_circolo,
        chiusa=prenotazione.chiusa,
    )


@router.post(
    "/prenotazioni/carica-foto-danni",
    response_model=list[str],
    summary="Carica le foto dei danni",
    description="Salva una o piu foto dei danni e restituisce i percorsi pubblici.",
    responses={
        200: {"description": "Foto caricate correttamente"},
        400: {"description": "Nessuna foto valida ricevuta"},
    },
)
async def carica_foto_danni(foto: list[UploadFile] = File(...)):
    PERCORSO_FOTO_DANNI.mkdir(parents=True, exist_ok=True)
    percorsi: list[str] = []

    for file in foto:
        if not file.filename:
            continue
        estensione = Path(file.filename).suffix.lower() or ".jpg"
        nome_file = f"danno-{uuid4().hex}{estensione}"
        destinazione = PERCORSO_FOTO_DANNI / nome_file
        contenuto = await file.read()
        destinazione.write_bytes(contenuto)
        percorsi.append(f"/archivio/danni/{nome_file}")

    if not percorsi:
        raise HTTPException(status_code=400, detail="Nessuna foto valida ricevuta")

    return percorsi


@router.get(
    "/registro-uscite",
    response_model=list[RegistroUscitaOutput],
    summary="Registro uscite",
    description="Storico completo di tutte le uscite registrate dal circolo.",
    responses={200: {"description": "Risposta completata"}},
)
def registro_uscite(db: Session = Depends(ottieni_db)):
    prenotazioni = (
        db.query(Prenotazione)
        .join(Utente, Prenotazione.id_creatore == Utente.id)
        .join(Risorsa, Prenotazione.id_risorsa == Risorsa.id)
        .order_by(Prenotazione.inizio.desc(), Prenotazione.id.desc())
        .all()
    )
    return [
        RegistroUscitaOutput(
            id=prenotazione.id,
            barca=prenotazione.risorsa.nome,
            tipologia=prenotazione.risorsa.tipologia,
            organizzatore=nome_completo_utente(prenotazione.creatore),
            data_uscita=prenotazione.inizio.date().isoformat(),
            ora_partenza=prenotazione.ora_partenza_effettiva,
            ora_arrivo=prenotazione.ora_rientro_effettiva,
            nota=prenotazione.nota,
            nota_rientro=prenotazione.nota_rientro,
            danni=prenotazione.danni,
            foto_danni=decodifica_foto_danni(prenotazione),
            persone_imbarcate=decodifica_persone_imbarcate(prenotazione),
            chiusa=prenotazione.chiusa,
        )
        for prenotazione in prenotazioni
    ]


@router.get(
    "/prenotazioni/disponibili",
    response_model=list[PrenotazioneDisponibileOutput],
    summary="Elenca le uscite aperte al circolo",
    description="Mostra tutte le uscite messe a disposizione del circolo, visibili a tutti i soci.",
    responses={200: {"description": "Risposta completata"}},
)
def elenco_uscite_disponibili(db: Session = Depends(ottieni_db)):
    prenotazioni = (
        db.query(Prenotazione)
        .join(Utente, Prenotazione.id_creatore == Utente.id)
        .join(Risorsa, Prenotazione.id_risorsa == Risorsa.id)
        .filter(
            Prenotazione.aperta_al_circolo.is_(True),
            Prenotazione.chiusa.is_(False),
        )
        .order_by(Prenotazione.inizio)
        .all()
    )

    return [
        PrenotazioneDisponibileOutput(
            id=prenotazione.id,
            barca=prenotazione.risorsa.nome,
            organizzatore=nome_completo_utente(prenotazione.creatore),
            ruolo_organizzatore=prenotazione.creatore.ruolo,
            inizio=prenotazione.inizio,
            fine=prenotazione.fine,
            nota=prenotazione.nota,
            persone_imbarcate=decodifica_persone_imbarcate(prenotazione),
            contatto_email=prenotazione.creatore.email,
            contatto_telefono=prenotazione.creatore.telefono,
        )
        for prenotazione in prenotazioni
    ]
