import os
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

# Must match the Django SECRET_KEY so tokens issued by Django can be verified here.
SECRET_KEY = os.getenv(
    "SECRET_KEY", "dev-only-insecure-secret-key-change-in-production-0123456789"
)
JWT_ALGORITHM = "HS256"

STATUSES = ["wishlist", "applied", "interview", "offer", "rejected"]


def normalize_database_url(url: str) -> str:
    """Convert any DATABASE_URL into an async SQLAlchemy URL.

    postgresql://u:p@host/db?sslmode=require -> postgresql+asyncpg://u:p@host/db?ssl=require
    Already-async URLs (postgresql+asyncpg://, sqlite+aiosqlite://) are returned unchanged.
    """
    if url.startswith(("postgres://", "postgresql://")):
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        sslmode = query.get("sslmode", [None])[0]
        new_query = {"ssl": "require"} if sslmode in ("require", "verify-ca", "verify-full") else {}
        if "host" in query:  # unix-socket style URL: keep the host parameter
            new_query["host"] = query["host"][0]
        return urlunparse(parsed._replace(scheme="postgresql+asyncpg", query=urlencode(new_query)))
    return url


# Preferred: the same DATABASE_URL you give Django. ANALYTICS_DATABASE_URL overrides it.
DATABASE_URL = normalize_database_url(
    os.getenv("ANALYTICS_DATABASE_URL")
    or os.getenv("DATABASE_URL")
    or "sqlite+aiosqlite:///../backend/db.sqlite3"
)
