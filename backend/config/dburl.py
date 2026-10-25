"""Tiny DATABASE_URL parser (no extra dependency)."""
from urllib.parse import parse_qs, unquote, urlparse


def parse_database_url(url: str) -> dict:
    """Turn postgres://user:pass@host:5432/dbname?sslmode=require into a Django DATABASES entry."""
    parsed = urlparse(url)
    if parsed.scheme not in ("postgres", "postgresql"):
        raise ValueError("DATABASE_URL must start with postgres:// or postgresql://")

    query = parse_qs(parsed.query)
    config = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": parsed.path.lstrip("/"),
        "USER": unquote(parsed.username or ""),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname or query.get("host", [""])[0],  # ?host=/socket/dir is also valid libpq
        "PORT": str(parsed.port or 5432),
    }
    sslmode = query.get("sslmode", [None])[0]
    if sslmode:
        config["OPTIONS"] = {"sslmode": sslmode}
    return config
