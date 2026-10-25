# Deploy JobTrack for free (Render + Neon)

Result: two public links, one for the Django API and one for the FastAPI analytics service.

- **Neon**: free hosted PostgreSQL (shared by both services)
- **Render**: runs the two Docker services from your GitHub repo

## 1. Create the database (Neon)

1. Sign up at https://neon.tech (you can use your GitHub login).
2. Create a project named `jobtrack`. Choose the region closest to you (for India, Singapore).
3. On the project dashboard, open **Connect** and copy the **connection string**. Turn **off** "Connection pooling" if the option is shown. It looks like:
   `postgresql://USER:PASSWORD@ep-xxxx.ap-southeast-1.aws.neon.tech/neondb?sslmode=require`
4. Keep it private. This is your `DATABASE_URL`.

## 2. Make a shared secret

Run this on your PC and copy the result. Both services must use the same value.

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

## 3. Deploy the Django API (Render)

1. Sign up at https://render.com with GitHub and allow access to your `jobtrack` repo.
2. Click **New +** > **Web Service** > pick the `jobtrack` repo.
3. Fill in:
   - **Name:** `jobtrack-api`
   - **Language:** Docker
   - **Branch:** `main`
   - **Region:** Singapore (any is fine)
   - **Root Directory:** leave empty
   - **Dockerfile Path:** `./backend/Dockerfile`
   - **Docker Build Context Directory:** `./backend`
   - **Instance Type:** Free
4. Under **Environment Variables**, add:

   | Key | Value |
   |---|---|
   | `SECRET_KEY` | the value from step 2 |
   | `DATABASE_URL` | your Neon connection string |
   | `DEBUG` | `0` |
   | `ALLOWED_HOSTS` | `*` |

5. Click **Create Web Service**. The first build takes about 5 minutes. Migrations run automatically on start.
6. When it says **Live**, open `https://jobtrack-api.onrender.com/` (your URL is shown at the top of the page). It should open the Swagger docs.

## 4. Deploy the FastAPI analytics service (Render)

Repeat step 3 with these changes:

- **Name:** `jobtrack-analytics`
- **Dockerfile Path:** `./analytics/Dockerfile`
- **Docker Build Context Directory:** `./analytics`
- **Environment Variables:** `SECRET_KEY` (same value as before) and `DATABASE_URL` (same Neon string)

Open `https://jobtrack-analytics.onrender.com/` and you should see its Swagger docs.

Deploy the Django API first, so its migrations create the table before analytics reads it.

## 5. Test the live links

With Python on your PC, run the demo against your live URLs (replace with your real URLs):

```powershell
$env:DJANGO_URL="https://jobtrack-api.onrender.com"
$env:ANALYTICS_URL="https://jobtrack-analytics.onrender.com"
python scripts/demo.py
```

You should see `Demo finished`. The first request can take about a minute (see below).

## 6. Add the links to GitHub and your resume

- Resume **Live Demo**: `https://jobtrack-api.onrender.com/api/docs/`
- Add both links near the top of your GitHub README under a "Live demo" heading.

## Free tier notes

- Free Render services go to sleep after about 15 minutes without traffic. The next visit takes up to a minute to wake them. Open your link yourself before an interview or before sharing it.
- Render's own free Postgres expires after a limited time, which is why this guide uses Neon. Check Neon's current free limits on its site.

## Troubleshooting

| Problem | Fix |
|---|---|
| Build fails with "Dockerfile not found" | Check Dockerfile Path is `./backend/Dockerfile` (or `./analytics/Dockerfile`) and the context directory is `./backend` (or `./analytics`) |
| Django shows "DisallowedHost" | Set `ALLOWED_HOSTS` to `*` and redeploy |
| Analytics returns 401 with a valid token | `SECRET_KEY` differs between the two services. Make them identical |
| Analytics returns 500 "relation does not exist" | Open the Django API once first and check its logs show migrations applied |
| Database connection or SSL errors | Check `DATABASE_URL` is the full string including `?sslmode=require`, with no spaces |
