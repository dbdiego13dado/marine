from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Risorsa(Base):
    __tablename__ = "risorse"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    tipologia = Column(String, nullable=True)
    descrizione = Column(String, nullable=True)

    prenotazioni = relationship("Prenotazione", back_populates="risorsa")
