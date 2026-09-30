from enum import Enum

from sqlalchemy import Boolean, Column, Enum as SqlEnum, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class RuoloUtente(str, Enum):
    ISTRUTTORE = "istruttore"
    ABILITATO = "abilitato"
    ALLIEVO = "allievo"


class Utente(Base):
    __tablename__ = "utenti"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cognome = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    telefono = Column(String, nullable=True)
    numero_tessera_fiv = Column(String, nullable=True)
    retta_annuale_in_regola = Column(Boolean, default=False, nullable=False)
    certificato_medico_consegnato = Column(Boolean, default=False, nullable=False)
    anno_validita_retta = Column(Integer, nullable=True)
    anno_validita_certificato = Column(Integer, nullable=True)
    ruolo = Column(SqlEnum(RuoloUtente), nullable=False)
    disponibile_per_circolo = Column(Boolean, default=False, nullable=False)
    nota_disponibilita = Column(Text, nullable=True)

    prenotazioni = relationship("Prenotazione", back_populates="creatore")
