from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Prenotazione(Base):
    __tablename__ = "prenotazioni"

    id = Column(Integer, primary_key=True, index=True)
    id_creatore = Column(Integer, ForeignKey("utenti.id"), nullable=False)
    id_risorsa = Column(Integer, ForeignKey("risorse.id"), nullable=False)
    inizio = Column(DateTime, nullable=False)
    fine = Column(DateTime, nullable=False)
    ora_partenza_effettiva = Column(DateTime, nullable=True)
    ora_rientro_effettiva = Column(DateTime, nullable=True)
    persone_imbarcate = Column(Text, nullable=True)
    nota = Column(Text, nullable=True)
    nota_rientro = Column(Text, nullable=True)
    danni = Column(Text, nullable=True)
    foto_danni = Column(Text, nullable=True)
    aperta_al_circolo = Column(Boolean, default=False, nullable=False)
    chiusa = Column(Boolean, default=False, nullable=False)

    creatore = relationship("Utente", back_populates="prenotazioni")
    risorsa = relationship("Risorsa", back_populates="prenotazioni")
