from datetime import date
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.configurazione import CONFIGURAZIONE_APP
from app.database import ottieni_db
from app.modelli.prenotazione import Prenotazione
from app.modelli.utente import RuoloUtente, Utente
from app.sicurezza import verifica_codice_amministratore

router = APIRouter(tags=["Utenti"])


class RegistrazioneUtente(BaseModel):
    nome: str = Field(..., description="Nome della persona")
    cognome: str = Field(..., description="Cognome della persona")
    email: EmailStr | None = Field(
        default=None,
        description="Email del socio, facoltativa se il telefono resta associato al profilo",
    )
    telefono: str | None = Field(default=None, description="Telefono di contatto")
    numero_tessera_fiv: str | None = Field(
        default=None,
        description="Numero tessera o codice associativo, facoltativo",
    )
    retta_annuale_in_regola: bool = Field(
        default=False,
        description="Indica se il socio e in regola con la retta annuale",
    )
    certificato_medico_consegnato: bool = Field(
        default=False,
        description="Indica se il certificato medico e stato consegnato",
    )
    ruolo: RuoloUtente = Field(..., description="Ruolo nel circolo")


class AggiornamentoUtente(BaseModel):
    nome: str = Field(..., description="Nome della persona")
    cognome: str = Field(..., description="Cognome della persona")
    email: EmailStr | None = Field(
        default=None,
        description="Email del socio, facoltativa",
    )
    telefono: str | None = Field(default=None, description="Telefono di contatto")
    numero_tessera_fiv: str | None = Field(
        default=None,
        description="Numero tessera o codice associativo, facoltativo",
    )
    retta_annuale_in_regola: bool = Field(
        default=False,
        description="Indica se il socio e in regola con la retta annuale",
    )
    certificato_medico_consegnato: bool = Field(
        default=False,
        description="Indica se il certificato medico e stato consegnato",
    )
    ruolo: RuoloUtente = Field(..., description="Ruolo nel circolo")


class AccessoUtente(BaseModel):
    email: EmailStr | None = Field(default=None, description="Email del socio")
    numero_tessera_fiv: str | None = Field(
        default=None, description="Numero tessera o codice associativo del socio"
    )


class UtenteOutput(BaseModel):
    id: int
    nome: str
    cognome: str | None
    email: str
    telefono: str | None
    numero_tessera_fiv: str | None
    retta_annuale_in_regola: bool
    certificato_medico_consegnato: bool
    anno_validita_retta: int | None
    anno_validita_certificato: int | None
    idoneo_anno_corrente: bool
    ruolo: RuoloUtente
    disponibile_per_circolo: bool
    nota_disponibilita: str | None

    model_config = {"from_attributes": True}


class UtenteAreaOutput(BaseModel):
    id: int
    nome: str
    cognome: str | None
    email: str
    telefono: str | None
    numero_tessera_fiv: str | None
    retta_annuale_in_regola: bool
    certificato_medico_consegnato: bool
    anno_validita_retta: int | None
    anno_validita_certificato: int | None
    idoneo_anno_corrente: bool
    ruolo: RuoloUtente
    disponibile_per_circolo: bool
    nota_disponibilita: str | None


class UtenteDisponibileOutput(BaseModel):
    id: int
    nome: str
    cognome: str | None
    ruolo: RuoloUtente
    email: str
    telefono: str | None
    nota_disponibilita: str | None


class ReportAmministratore(BaseModel):
    anno_corrente: int
    totale_soci: int
    soci_in_regola_con_retta: int
    soci_con_certificato: int
    soci_disponibili_per_circolo: int
    totale_prenotazioni: int
    utenti: list[UtenteOutput]


class IdoneitaAnnualeUtente(BaseModel):
    retta_annuale_in_regola: bool = Field(default=False)
    certificato_medico_consegnato: bool = Field(default=False)
    anno_validita: int | None = Field(default=None)


def anno_corrente() -> int:
    return date.today().year


def retta_valida(utente: Utente) -> bool:
    return bool(
        utente.retta_annuale_in_regola
        and utente.anno_validita_retta == anno_corrente()
    )


def certificato_valido(utente: Utente) -> bool:
    return bool(
        utente.certificato_medico_consegnato
        and utente.anno_validita_certificato == anno_corrente()
    )


def utente_idoneo(utente: Utente) -> bool:
    return retta_valida(utente) and certificato_valido(utente)


def utente_output(utente: Utente) -> UtenteOutput:
    return UtenteOutput(
        id=utente.id,
        nome=utente.nome,
        cognome=utente.cognome,
        email=utente.email,
        telefono=utente.telefono,
        numero_tessera_fiv=utente.numero_tessera_fiv,
        retta_annuale_in_regola=retta_valida(utente),
        certificato_medico_consegnato=certificato_valido(utente),
        anno_validita_retta=utente.anno_validita_retta,
        anno_validita_certificato=utente.anno_validita_certificato,
        idoneo_anno_corrente=utente_idoneo(utente),
        ruolo=utente.ruolo,
        disponibile_per_circolo=utente.disponibile_per_circolo,
        nota_disponibilita=utente.nota_disponibilita,
    )


def utente_area_output(utente: Utente) -> UtenteAreaOutput:
    return UtenteAreaOutput(**utente_output(utente).model_dump())


def genera_email_interna() -> str:
    return f"socio-{uuid4().hex}@{CONFIGURAZIONE_APP['dominio_email_interna']}"


def genera_tessera_interna() -> str:
    return f"APP-{uuid4().hex[:10].upper()}"


@router.post(
    "/utenti",
    response_model=UtenteOutput,
    status_code=status.HTTP_201_CREATED,
    summary="Registra un utente",
    description="Crea il profilo iniziale di un istruttore, abilitato o allievo.",
    responses={
        201: {"description": "Utente registrato con successo"},
        400: {"description": "Richiesta non valida"},
    },
)
def registra_utente(payload: RegistrazioneUtente, db: Session = Depends(ottieni_db)):
    email_registrata = str(payload.email).strip() if payload.email else genera_email_interna()
    while db.query(Utente).filter(Utente.email == email_registrata).first() is not None:
        email_registrata = genera_email_interna()

    tessera_registrata = (
        payload.numero_tessera_fiv.strip()
        if payload.numero_tessera_fiv and payload.numero_tessera_fiv.strip()
        else genera_tessera_interna()
    )
    while (
        db.query(Utente)
        .filter(Utente.numero_tessera_fiv == tessera_registrata)
        .first()
        is not None
    ):
        tessera_registrata = genera_tessera_interna()

    utente = Utente(
        nome=payload.nome,
        cognome=payload.cognome,
        email=email_registrata,
        telefono=payload.telefono,
        numero_tessera_fiv=tessera_registrata,
        retta_annuale_in_regola=False,
        certificato_medico_consegnato=False,
        anno_validita_retta=None,
        anno_validita_certificato=None,
        ruolo=payload.ruolo,
    )
    db.add(utente)
    db.commit()
    db.refresh(utente)
    return utente_output(utente)


@router.post(
    "/utenti/accesso",
    response_model=UtenteAreaOutput,
    summary="Accedi come socio",
    description="Identifica il socio tramite email o tessera per mostrare solo le sue azioni.",
    responses={
        200: {"description": "Accesso consentito"},
        403: {"description": "Credenziali non valide"},
    },
)
def accesso_utente(payload: AccessoUtente, db: Session = Depends(ottieni_db)):
    if payload.email is None and payload.numero_tessera_fiv is None:
        raise HTTPException(
            status_code=400,
            detail="Inserisci almeno email oppure numero tessera",
        )

    utente = None

    if payload.email is not None and payload.numero_tessera_fiv is not None:
        utente = (
            db.query(Utente)
            .filter(
                Utente.email == str(payload.email),
                Utente.numero_tessera_fiv == payload.numero_tessera_fiv,
            )
            .first()
        )

    if utente is None and payload.email is not None:
        utente = db.query(Utente).filter(Utente.email == str(payload.email)).first()

    if utente is None and payload.numero_tessera_fiv is not None:
        utente = (
            db.query(Utente)
            .filter(Utente.numero_tessera_fiv == payload.numero_tessera_fiv)
            .first()
        )

    if utente is None and payload.email is not None and payload.numero_tessera_fiv is not None:
        utente = (
            db.query(Utente)
            .filter(
                or_(
                    Utente.email == str(payload.email),
                    Utente.numero_tessera_fiv == payload.numero_tessera_fiv,
                )
            )
            .first()
        )

    if utente is None:
        raise HTTPException(status_code=403, detail="Email o tessera non validi")
    return utente_area_output(utente)


@router.get(
    "/utenti/prova",
    response_model=UtenteAreaOutput,
    summary="Accesso rapido di prova",
    description="Durante i test apre il primo socio disponibile.",
    responses={
        200: {"description": "Accesso rapido consentito"},
        404: {"description": "Nessun socio disponibile"},
    },
)
def accesso_rapido_prova(db: Session = Depends(ottieni_db)):
    utente = db.query(Utente).order_by(Utente.id.asc()).first()
    if utente is None:
        raise HTTPException(status_code=404, detail="Nessun socio disponibile")
    return utente_area_output(utente)


@router.put(
    "/utenti/{id_utente}",
    response_model=UtenteAreaOutput,
    summary="Aggiorna i dati del socio",
    description="Permette al socio di modificare i propri dati di iscrizione in qualsiasi momento.",
    responses={
        200: {"description": "Dati aggiornati con successo"},
        400: {"description": "Richiesta non valida"},
        404: {"description": "Utente non trovato"},
    },
)
def aggiorna_utente(id_utente: int, payload: AggiornamentoUtente, db: Session = Depends(ottieni_db)):
    utente = db.query(Utente).filter(Utente.id == id_utente).first()
    if utente is None:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    email_aggiornata = str(payload.email).strip() if payload.email else utente.email
    if not email_aggiornata:
        email_aggiornata = genera_email_interna()
        while db.query(Utente).filter(Utente.email == email_aggiornata).first() is not None:
            email_aggiornata = genera_email_interna()

    tessera_aggiornata = (
        payload.numero_tessera_fiv.strip()
        if payload.numero_tessera_fiv and payload.numero_tessera_fiv.strip()
        else utente.numero_tessera_fiv
    )
    if not tessera_aggiornata:
        tessera_aggiornata = genera_tessera_interna()
        while (
            db.query(Utente)
            .filter(Utente.numero_tessera_fiv == tessera_aggiornata)
            .first()
            is not None
        ):
            tessera_aggiornata = genera_tessera_interna()

    email_esistente = (
        db.query(Utente)
        .filter(Utente.email == email_aggiornata, Utente.id != id_utente)
        .first()
    )
    if email_esistente is not None:
        raise HTTPException(status_code=400, detail="Esiste gia un utente con questa email")

    tessera_esistente = (
        db.query(Utente)
        .filter(Utente.numero_tessera_fiv == tessera_aggiornata, Utente.id != id_utente)
        .first()
    )
    if tessera_esistente is not None:
        raise HTTPException(status_code=400, detail="Esiste gia un socio con questa tessera")

    utente.nome = payload.nome
    utente.cognome = payload.cognome
    utente.email = email_aggiornata
    utente.telefono = payload.telefono
    utente.numero_tessera_fiv = tessera_aggiornata
    utente.ruolo = payload.ruolo
    db.commit()
    db.refresh(utente)
    return utente_area_output(utente)


@router.get(
    "/utenti",
    response_model=list[UtenteOutput],
    summary="Elenca tutti gli utenti",
    description="Elenco completo riservato all'amministratore.",
    responses={
        200: {"description": "Risposta completata"},
        403: {"description": "Accesso amministratore non autorizzato"},
    },
    dependencies=[Depends(verifica_codice_amministratore)],
)
def elenco_utenti(db: Session = Depends(ottieni_db)):
    utenti = db.query(Utente).order_by(Utente.cognome, Utente.nome).all()
    return [utente_output(utente) for utente in utenti]


@router.get(
    "/utenti/disponibili",
    response_model=list[UtenteDisponibileOutput],
    summary="Elenca le persone disponibili per il circolo",
    description="Mostra istruttori e abilitati disponibili, visibili agli altri soci.",
    responses={200: {"description": "Risposta completata"}},
)
def elenco_utenti_disponibili(db: Session = Depends(ottieni_db)):
    utenti = (
        db.query(Utente)
        .filter(
            Utente.disponibile_per_circolo.is_(True),
            Utente.ruolo.in_([RuoloUtente.ISTRUTTORE, RuoloUtente.ABILITATO]),
        )
        .order_by(Utente.cognome, Utente.nome)
        .all()
    )
    return [
        UtenteDisponibileOutput(
            id=utente.id,
            nome=utente.nome,
            cognome=utente.cognome,
            ruolo=utente.ruolo,
            email=utente.email,
            telefono=utente.telefono,
            nota_disponibilita=utente.nota_disponibilita,
        )
        for utente in utenti
    ]


@router.put(
    "/amministrazione/utenti/{id_utente}/idoneita",
    response_model=UtenteOutput,
    summary="Aggiorna idoneità annuale socio",
    description="Permette solo all'amministratore di sbloccare o bloccare un socio per l'anno corrente.",
    responses={
        200: {"description": "Idoneità aggiornata"},
        404: {"description": "Utente non trovato"},
        403: {"description": "Accesso amministratore non autorizzato"},
    },
    dependencies=[Depends(verifica_codice_amministratore)],
)
def aggiorna_idoneita_annuale(
    id_utente: int,
    payload: IdoneitaAnnualeUtente,
    db: Session = Depends(ottieni_db),
):
    utente = db.query(Utente).filter(Utente.id == id_utente).first()
    if utente is None:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    anno = payload.anno_validita or anno_corrente()
    utente.retta_annuale_in_regola = payload.retta_annuale_in_regola
    utente.certificato_medico_consegnato = payload.certificato_medico_consegnato
    utente.anno_validita_retta = anno if payload.retta_annuale_in_regola else None
    utente.anno_validita_certificato = anno if payload.certificato_medico_consegnato else None
    if not utente_idoneo(utente):
        utente.disponibile_per_circolo = False
        utente.nota_disponibilita = None
    db.commit()
    db.refresh(utente)
    return utente_output(utente)


@router.get(
    "/amministrazione/report",
    response_model=ReportAmministratore,
    summary="Report amministratore",
    description="Riepilogo completo per presidente o amministratore.",
    responses={
        200: {"description": "Risposta completata"},
        403: {"description": "Accesso amministratore non autorizzato"},
    },
    dependencies=[Depends(verifica_codice_amministratore)],
)
def report_amministratore(db: Session = Depends(ottieni_db)):
    utenti = db.query(Utente).order_by(Utente.cognome, Utente.nome).all()
    totale_prenotazioni = db.query(Prenotazione).count()
    return ReportAmministratore(
        anno_corrente=anno_corrente(),
        totale_soci=len(utenti),
        soci_in_regola_con_retta=sum(1 for utente in utenti if retta_valida(utente)),
        soci_con_certificato=sum(1 for utente in utenti if certificato_valido(utente)),
        soci_disponibili_per_circolo=sum(1 for utente in utenti if utente.disponibile_per_circolo),
        totale_prenotazioni=totale_prenotazioni,
        utenti=[utente_output(utente) for utente in utenti],
    )
