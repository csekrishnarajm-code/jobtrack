# JobTrack

A job application tracker with two backend services: a Django REST API where I store my applications, and a separate FastAPI service that turns that data into simple analytics (how many applications are at each stage, how many I sent each week, which interviews are coming up).

**Live demo (free hosting, the first request can take up to a minute to wake up):**

- Django API + Swagger: https://jobtracker-zlng.onrender.com/api/docs/
- FastAPI analytics + Swagger: https://jobtrack-analytics.onrender.com/docs

## Why I built this

I'm a fresher applying for Python developer roles, so I wanted a project I would actually use during my own job search. My earlier projects were built with Flask. This time I wanted hands-on practice with Django REST Framework, FastAPI, PostgreSQL, Docker and a real deployment, all in one project instead of separate small demos.

## How it works

There are two services and one PostgreSQL database.

- **`backend/` (Django + DRF)** handles registration, login (JWT) and the CRUD for applications. It also owns the database schema and migrations.
- **`analytics/` (FastAPI)** only reads from the same database. It checks the JWT that Django issued and returns numbers for that user only.

A user logs in once on the Django side and uses the same token on both services.

## What it can do

- Register and log in with JWT. Passwords are hashed and checked with Django's validators.
- Add, edit, delete and list applications with a status: wishlist, applied, interview, offer or rejected.
- Filter by status, search by company, role or location, sort, and paginate the list.
- Each user can only see their own applications.
- Analytics: counts per status with interview and offer rates, applications per week, and the next 10 interviews.
- Swagger docs for both services.

## Try it

1. Open the Django docs and register with `POST /api/auth/register/`.
2. Log in with `POST /api/auth/login/` and copy the `access` token.
3. Click **Authorize** and paste the token. Add a few applications with `POST /api/applications/`.
4. Open the analytics docs, click **Authorize**, paste the same token, and try `/analytics/summary`.

## Run it on your machine

You need Docker.

```bash
cp .env.example .env      # then set SECRET_KEY and POSTGRES_PASSWORD
docker compose up --build
```

- Django: http://localhost:8000/api/docs/
- FastAPI: http://localhost:8001/docs

With the services running, `python scripts/demo.py` registers a user, adds sample applications and calls both services. Captured output is in [docs/SAMPLE_OUTPUT.md](docs/SAMPLE_OUTPUT.md).

## API

Django (port 8000)

| Method | Endpoint | What it does |
|---|---|---|
| POST | `/api/auth/register/` | create an account |
| POST | `/api/auth/login/` | get access and refresh tokens |
| POST | `/api/auth/refresh/` | get a new access token |
| GET, POST | `/api/applications/` | list (filter, search, order, page) or create |
| GET, PUT, PATCH, DELETE | `/api/applications/{id}/` | read, update or delete one application |

FastAPI (port 8001)

| Method | Endpoint | What it does |
|---|---|---|
| GET | `/analytics/summary` | count per status, interview rate, offer rate |
| GET | `/analytics/weekly?weeks=8` | applications per week |
| GET | `/analytics/upcoming-interviews` | next 10 interviews |
| GET | `/health` | health check |

Interview rate means (interview + offer) divided by applications actually submitted, so wishlist items are not counted.

## Decisions I made

- **Django owns the database, FastAPI only reads it.** I did not want two services both changing the schema.
- **Both services share one `SECRET_KEY` and verify the same HS256 JWT.** It is the simplest option for two services I control. With more services I would switch to asymmetric keys so only one service can sign tokens.
- **Every analytics query is filtered by the `user_id` inside the token**, so one user can never see another user's numbers. There is a test for this.
- **The analytics endpoints are `async`** and use SQLAlchemy's async engine with `asyncpg`.

## Problems I ran into

- **Deploying two services from one repo on Render.** My first deploy failed because the Dockerfile path and build context did not match the folder layout in GitHub. Each service needs its own Dockerfile path (`./backend/Dockerfile`, `./analytics/Dockerfile`) and build context.
- **Database URLs.** Neon gives a connection string with `sslmode=require`, but `asyncpg` expects `ssl=require`. I added a small function in `analytics/app/config.py` to convert the URL, and unit tests for it.
- **Free tier sleep.** Render's free services sleep when idle, which is why the first request is slow.

## Tests

```bash
cd backend   && pytest -q     # 13 tests
cd analytics && pytest -q     # 11 tests
```

They cover registration and login, weak and duplicate input, CRUD, data isolation between users, filtering and search, JWT checks on the analytics side, and the rate and weekly calculations. A GitHub Actions workflow runs both suites on every push.

## What I want to add next

- A React frontend that talks to this API
- Refresh-token handling on the client
- Redis caching for the analytics endpoints
- Rate limiting on login
- Automatic deploys after the tests pass

## Project structure

```
jobtrack/
├── backend/        Django + DRF (models, serializers, views, tests)
├── analytics/      FastAPI (JWT auth, async DB access, tests)
├── docs/           deployment guide and sample output
├── scripts/        demo.py
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## About me

Krishnaraj M, fresher Python developer from Hosur, Tamil Nadu.
[LinkedIn](https://linkedin.com/in/krishnaraj-m) | [GitHub](https://github.com/csekrishnarajm-code) | csekrishnarajm@gmail.com
