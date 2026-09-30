# Marine - MarinaSuite SaaS MVP

Versione **0.1.0**. Gestionale per darsene, posti barca e prenotazioni.

Repository: https://github.com/dbdiego13dado/marine

La cronologia delle versioni e in `CHANGELOG.md`; il tag `v0.1.0` identifica
la prima importazione. Il database SQLite e i dati demo vengono creati
automaticamente al primo avvio. Database e upload gia presenti sul PC
non sono inclusi nella repository.

FastAPI MVP for an international SaaS platform serving marinas, docks, small tourist ports, and nautical storage businesses.

## Stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- SQLite
- Jinja2 templates
- Pydantic schemas
- Signed cookie sessions
- Secure PBKDF2 password hashing
- Uvicorn

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Demo Credentials

All demo users use:

```text
Demo12345!
```

Accounts:

- `super@marinasuite.demo` - super_admin
- `admin@marinasuite.demo` - marina_admin
- `staff@marinasuite.demo` - staff
- `customer@marinasuite.demo` - customer

## Included Demo Data

- 3 SaaS plans: free, pro, premium
- 1 demo marina
- 4 demo users
- 100 berth slots (20 transient, 70 owner, 10 service/maintenance)
- 2 boats
- 3 bookings
- 1 paid mock payment
- 1 clickable marina map with berth positions

## Main API Routes

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /users`, `POST /users`
- `GET /marinas`, `POST /marinas`
- `GET /plans`
- `GET /berths`, `POST /berths`
- `GET /boats`, `POST /boats`
- `GET /bookings`, `POST /bookings`
- `GET /payments`, `POST /payments/mock-checkout`
- `GET /maps`, `GET /maps/{id}`
- `GET /dashboard/summary`

## UI Pages

- `/login`
- `/register`
- `/dashboard`
- `/customer`
- `/ui/berths`
- `/ui/boats`
- `/ui/bookings`
- `/map`

## Note sulla versione

Questa e una versione MVP dimostrativa: gli account demo vengono creati
automaticamente e i pagamenti sono simulati. `SESSION_SECRET` configura
la chiave delle sessioni tramite una variabile d'ambiente.

`ISTRUZIONI_PERSONALIZZAZIONE.md`, `configurazione_cliente.example.json` e i
moduli italiani storici sono conservati come parte del progetto originale;
le relative istruzioni riguardano la precedente app di prenotazione
imbarcazioni. L'applicazione attiva e `app.main:app`, MarinaSuite SaaS MVP.
