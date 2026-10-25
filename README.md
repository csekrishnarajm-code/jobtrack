# JobTrack - Job Application Tracker (Django REST Framework + FastAPI)

A backend project made of two cooperating services that share one PostgreSQL database and one JWT secret:

| Service | Tech | Port | Purpose |
|---|---|---|---|
| `backend/` | Django, Django REST Framework, SimpleJWT | 8000 | Auth + CRUD for job applications, Django admin, Swagger docs |
| `analytics/` | FastAPI, async SQLAlchemy, asyncpg | 8001 | Async analytics endpoints (summary, weekly trend, upcoming interviews), Swagger docs |
| `db` | PostgreSQL 16 | - | Shared database |

```
        register / login (JWT)                       analytics (same JWT)
 Client ----------------------> Django REST API      Client -----------> FastAPI service
                                     |                                        |
                                     +------------- PostgreSQL <--------------+
                                    (writes, owns migrations)            (async reads)
```

## Features

- User registration and login with JWT (hashed passwords, Django password validators)
- CRUD for applications: company, role, status (`wishlist`, `applied`, `interview`, `offer`, `rejected`), location, job URL, notes, applied/interview dates
- Per-user data isolation: users can only see and change their own applications
- Filtering (`?status=`), search (`?search=`), ordering (`?ordering=`) and pagination
- Swagger/OpenAPI docs for both services
- FastAPI service verifies the Django-issued JWT and returns only the caller's analytics
- Automated tests (pytest) for both services, Docker Compose setup, GitHub Actions CI

## Live demo


   - Django API + Swagger: https://jobtracker-zlng.onrender.com/api/docs/
   - FastAPI analytics + Swagger: https://jobtrack-analytics.onrender.com/docs

(Free hosting sleeps when idle, so the first request can take about a minute.)

## Run with Docker (recommended)

```bash
cp .env.example .env        # then edit SECRET_KEY and POSTGRES_PASSWORD
docker compose up --build
```

- Django API + Swagger: http://localhost:8000/api/docs/
- FastAPI analytics + Swagger: http://localhost:8001/docs
- Django admin: http://localhost:8000/admin/ (create a user first: `docker compose exec backend python manage.py createsuperuser`)

## Run locally without Docker (SQLite)

```bash
# Terminal 1 - Django
cd backend
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000

# Terminal 2 - FastAPI (reads Django's SQLite file)
cd analytics
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8001
```

## Quick demo (one command)

With the project running, this registers a user, logs in, creates sample applications and calls both services:

```bash
python scripts/demo.py
```

See real captured output in [docs/SAMPLE_OUTPUT.md](docs/SAMPLE_OUTPUT.md).

## Try it manually

```bash
# 1. Register and log in
curl -X POST localhost:8000/api/auth/register/ -H "Content-Type: application/json" \
  -d '{"username":"krish","email":"krish@example.com","password":"StrongPass123!"}'

curl -X POST localhost:8000/api/auth/login/ -H "Content-Type: application/json" \
  -d '{"username":"krish","password":"StrongPass123!"}'
# -> {"refresh": "...", "access": "<TOKEN>"}

# 2. Add applications
curl -X POST localhost:8000/api/applications/ \
  -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"company":"Zoho","role":"Python Developer","status":"interview","applied_date":"2026-10-05","interview_date":"2026-10-20"}'

# 3. List / filter / search
curl "localhost:8000/api/applications/?status=interview" -H "Authorization: Bearer <TOKEN>"
curl "localhost:8000/api/applications/?search=zoho&ordering=-applied_date" -H "Authorization: Bearer <TOKEN>"

# 4. Analytics from the FastAPI service (same token)
curl localhost:8001/analytics/summary -H "Authorization: Bearer <TOKEN>"
curl "localhost:8001/analytics/weekly?weeks=8" -H "Authorization: Bearer <TOKEN>"
curl localhost:8001/analytics/upcoming-interviews -H "Authorization: Bearer <TOKEN>"
```

In Swagger, click **Authorize** and paste the access token to try endpoints in the browser.

## API reference

**Django (port 8000)**

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Create account |
| POST | `/api/auth/login/` | Get access + refresh tokens |
| POST | `/api/auth/refresh/` | Get a new access token |
| GET/POST | `/api/applications/` | List (filter/search/order/paginate) / create |
| GET/PUT/PATCH/DELETE | `/api/applications/{id}/` | Retrieve / update / delete |

**FastAPI (port 8001)**

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/analytics/summary` | Count per status, interview rate, offer rate |
| GET | `/analytics/weekly?weeks=8` | Applications per week (zero-filled) |
| GET | `/analytics/upcoming-interviews` | Next 10 interviews |

Interview rate = (interview + offer) / submitted applications; "submitted" excludes `wishlist`.

## Tests

```bash
cd backend   && pytest -q     # 13 tests: auth, CRUD, isolation, filtering, validation, DB URL parsing
cd analytics && pytest -q     # 11 tests: JWT checks, summary, weekly, upcoming, URL handling
```

## Project structure

```
jobtrack/
├── backend/                 # Django + DRF
│   ├── config/              # settings, urls, wsgi
│   ├── applications/        # models, serializers, views, tests
│   ├── Dockerfile
│   └── requirements.txt
├── analytics/               # FastAPI
│   ├── app/                 # main, auth (JWT), db, schemas, config
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── docs/DEPLOY.md           # free live deployment guide
├── scripts/demo.py          # one-command demo
├── docs/SAMPLE_OUTPUT.md    # captured output + test results
├── docker-compose.yml
├── .env.example
└── .github/workflows/ci.yml
```

## Design notes

- Django owns the schema and migrations; the FastAPI service only reads the `job_applications` table.
- Both services use the same `SECRET_KEY` (HS256). FastAPI validates the signature, expiry and `token_type == "access"`, then filters every query by the token's `user_id`.
- FastAPI endpoints are `async` and use SQLAlchemy's async engine with `asyncpg`.
