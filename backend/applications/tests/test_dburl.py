import pytest

from config.dburl import parse_database_url


def test_parses_neon_style_url():
    cfg = parse_database_url(
        "postgresql://neon_user:p%40ss@ep-cool-123.ap-south-1.aws.neon.tech/neondb?sslmode=require"
    )
    assert cfg["ENGINE"] == "django.db.backends.postgresql"
    assert cfg["NAME"] == "neondb"
    assert cfg["USER"] == "neon_user"
    assert cfg["PASSWORD"] == "p@ss"  # URL-encoded characters are decoded
    assert cfg["HOST"] == "ep-cool-123.ap-south-1.aws.neon.tech"
    assert cfg["PORT"] == "5432"
    assert cfg["OPTIONS"] == {"sslmode": "require"}


def test_url_without_ssl_and_custom_port():
    cfg = parse_database_url("postgres://u:p@localhost:6543/db")
    assert cfg["PORT"] == "6543"
    assert "OPTIONS" not in cfg


def test_rejects_other_schemes():
    with pytest.raises(ValueError):
        parse_database_url("mysql://u:p@h/db")


def test_root_redirects_to_docs(client):
    res = client.get("/")
    assert res.status_code == 302
    assert res["Location"] == "/api/docs/"
