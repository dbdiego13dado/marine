# Prenotazioni Imbarcazioni - base personalizzabile

Questa versione e pensata come base neutra: ogni circolo puo cambiare nome, logo testuale, contatti, orari, regolamento, password amministratore e flotta senza modificare il codice principale.

Puoi farlo in due modi:

- Dal browser, entrando in `Amministratore` con la password e usando la sezione `Personalizzazione app`.
- Dal file `configurazione_cliente.json`, se vuoi preparare una configurazione prima di consegnare l'app.

## Come personalizzare l'app

1. Duplica il file `configurazione_cliente.example.json`.
2. Rinominalo in `configurazione_cliente.json`.
3. Modifica i valori dentro `configurazione_cliente.json`.
4. Riavvia l'app.

Se `configurazione_cliente.json` non esiste, l'app usa la configurazione neutra predefinita.

## Cosa puoi cambiare

- `nome_app`: nome completo dell'app.
- `nome_breve`: nome corto usato nel manifest della app installabile.
- `logo`: le tre righe del logo testuale in alto.
- `home`: testi della schermata iniziale.
- `contatti`: telefono, email, sede e citta.
- `orari`: apertura e chiusura della sede o del servizio.
- `database_nome`: nome del database SQLite del cliente.
- `dominio_email_interna`: dominio usato per creare email tecniche quando il socio non inserisce la mail.
- `codice_amministratore`: password dell'area amministratore.
- `percorso_regolamento`: percorso del PDF che si apre dal pulsante Regolamento.
- `categorie_barche`: categorie e nomi delle imbarcazioni disponibili.

## Esempio flotta

```json
"categorie_barche": [
  {
    "codice": "derive",
    "etichetta": "Derive",
    "barche": ["Deriva 1", "Deriva 2", "Deriva 3"]
  },
  {
    "codice": "gommoni",
    "etichetta": "Gommoni",
    "barche": ["Gommone 1", "Gommone 2"]
  }
]
```

Il `codice` deve essere scritto senza spazi. L'`etichetta` e il testo che vede l'utente.

## Avvio in locale

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8025 --reload
```

Poi apri:

```text
http://127.0.0.1:8025/
```

## Preparazione per App Store e Play Store

Per pubblicare su App Store e Play Store non basta il server FastAPI sul PC. Serve:

- un backend online stabile con HTTPS, per esempio server cloud;
- un'app mobile nativa o un contenitore mobile, per esempio Capacitor, che apra l'interfaccia e comunichi con il backend;
- icone, splash screen, nome pacchetto Android e bundle identifier iOS per ogni cliente;
- account sviluppatore Apple e Google Play;
- privacy policy, termini, descrizione app e schermate per gli store.

La base attuale e gia impostata come PWA/web app. Il prossimo passo tecnico consigliato e creare una cartella mobile con Capacitor e collegarla all'indirizzo HTTPS definitivo del backend.

Riferimenti ufficiali utili:

- Apple App Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- Google Play target API level: https://developer.android.com/google/play/requirements/target-sdk
- Android App Bundle: https://developer.android.com/guide/app-bundle
- Capacitor: https://capacitorjs.com/docs
