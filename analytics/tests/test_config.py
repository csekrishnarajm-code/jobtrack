from app.config import normalize_database_url


def test_converts_neon_url_for_asyncpg():
    out = normalize_database_url(
        "postgresql://user:pw@ep-x.neon.tech/neondb?sslmode=require&channel_binding=require"
    )
    assert out == "postgresql+asyncpg://user:pw@ep-x.neon.tech/neondb?ssl=require"


def test_plain_postgres_url_without_ssl():
    assert (
        normalize_database_url("postgres://u:p@db:5432/jobtrack")
        == "postgresql+asyncpg://u:p@db:5432/jobtrack"
    )


def test_async_urls_unchanged():
    url = "postgresql+asyncpg://u:p@db:5432/x"
    assert normalize_database_url(url) == url
    assert normalize_database_url("sqlite+aiosqlite:///x.db") == "sqlite+aiosqlite:///x.db"
