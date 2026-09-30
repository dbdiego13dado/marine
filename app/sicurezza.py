from secrets import compare_digest

from fastapi import Header, HTTPException, status

from app.configurazione import codice_amministratore


def verifica_codice_amministratore(
    x_codice_amministratore: str | None = Header(default=None, alias="X-Codice-Amministratore"),
) -> None:
    codice_atteso = codice_amministratore()
    if x_codice_amministratore is None or not compare_digest(
        x_codice_amministratore, codice_atteso
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accesso amministratore non autorizzato",
        )
