"""
JobTrack demo: register -> login -> create applications -> call the analytics service.

Needs only Python 3 (no extra packages). Make sure the project is running first
(docker compose up), then run:

    python scripts/demo.py
"""
import json
import os
import urllib.error
import urllib.request
from datetime import date, timedelta

DJANGO = os.getenv("DJANGO_URL", "http://localhost:8000")
ANALYTICS = os.getenv("ANALYTICS_URL", "http://localhost:8001")
USER = {"username": "demo", "email": "demo@example.com", "password": "StrongPass123!"}


def call(method, url, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")
    except urllib.error.URLError as e:
        raise SystemExit(f"Cannot reach {url}\nIs the project running? (docker compose up)\n{e}")


def show(title, status, data):
    print(f"\n=== {title}  (HTTP {status}) ===")
    print(json.dumps(data, indent=2))


def main():
    today = date.today()

    status, data = call("POST", f"{DJANGO}/api/auth/register/", USER)
    show("1. Register user", status, data)  # 400 just means the user already exists

    status, data = call(
        "POST",
        f"{DJANGO}/api/auth/login/",
        {"username": USER["username"], "password": USER["password"]},
    )
    if status != 200:
        print("Login failed:", data)
        return
    token = data["access"]
    print(f"\n=== 2. Login  (HTTP {status}) ===\nGot access token: {token[:25]}...")

    status, data = call("GET", f"{DJANGO}/api/applications/", token=token)
    if data["count"] == 0:
        samples = [
            {"company": "Zoho", "role": "Python Developer", "status": "interview",
             "applied_date": str(today - timedelta(days=4)),
             "interview_date": str(today + timedelta(days=6))},
            {"company": "Freshworks", "role": "Backend Developer", "status": "applied",
             "applied_date": str(today - timedelta(days=2))},
            {"company": "Infosys", "role": "Python Developer", "status": "offer",
             "applied_date": str(today - timedelta(days=12))},
            {"company": "TCS", "role": "Software Engineer", "status": "rejected",
             "applied_date": str(today - timedelta(days=18))},
            {"company": "Google", "role": "Software Engineer", "status": "wishlist"},
        ]
        for s in samples:
            code, _ = call("POST", f"{DJANGO}/api/applications/", s, token)
            print(f"\n=== 3. Create {s['company']} / {s['role']}  (HTTP {code}) ===")
    else:
        print("\n=== 3. Applications already exist, skipping creation ===")

    status, data = call("GET", f"{DJANGO}/api/applications/?status=interview", token=token)
    show("4. Django: filter applications by status=interview", status, data)

    status, data = call("GET", f"{DJANGO}/api/applications/?search=python&ordering=company", token=token)
    show("5. Django: search 'python', ordered by company", status, data)

    status, data = call("GET", f"{ANALYTICS}/analytics/summary", token=token)
    show("6. FastAPI: /analytics/summary", status, data)

    status, data = call("GET", f"{ANALYTICS}/analytics/weekly?weeks=4", token=token)
    show("7. FastAPI: /analytics/weekly?weeks=4", status, data)

    status, data = call("GET", f"{ANALYTICS}/analytics/upcoming-interviews", token=token)
    show("8. FastAPI: /analytics/upcoming-interviews", status, data)

    status, _ = call("GET", f"{ANALYTICS}/analytics/summary")
    print(f"\n=== 9. FastAPI without a token  (HTTP {status}) - correctly rejected ===")

    print("\nDemo finished. Everything above came from a live run of the project.")


if __name__ == "__main__":
    main()
