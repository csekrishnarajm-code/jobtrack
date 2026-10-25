import os
import tempfile
from datetime import date, timedelta

# Must be set BEFORE the app is imported.
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["ANALYTICS_DATABASE_URL"] = f"sqlite+aiosqlite:///{_tmp.name}"
os.environ["SECRET_KEY"] = "test-secret-key-that-is-long-enough-for-hs256-0123456789"

import jwt  # noqa: E402
import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.db import SessionLocal, applications, engine, metadata  # noqa: E402
from app.main import app  # noqa: E402


def make_token(user_id: int, token_type: str = "access", secret: str | None = None):
    return jwt.encode(
        {"user_id": user_id, "token_type": token_type},
        secret or os.environ["SECRET_KEY"],
        algorithm="HS256",
    )


@pytest.fixture
def token():
    return make_token


@pytest_asyncio.fixture(autouse=True)
async def database():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

    today = date.today()
    rows = [
        # user 1
        dict(user_id=1, company="Zoho", role="Dev", status="applied", applied_date=today, interview_date=None),
        dict(user_id=1, company="Freshworks", role="Dev", status="interview", applied_date=today - timedelta(weeks=1), interview_date=today + timedelta(days=3)),
        dict(user_id=1, company="Infosys", role="Dev", status="offer", applied_date=today - timedelta(weeks=2), interview_date=today - timedelta(days=5)),
        dict(user_id=1, company="TCS", role="Dev", status="rejected", applied_date=today - timedelta(weeks=3), interview_date=None),
        dict(user_id=1, company="Google", role="Dev", status="wishlist", applied_date=None, interview_date=None),
        # user 2 (must never leak into user 1's numbers)
        dict(user_id=2, company="Other", role="Dev", status="applied", applied_date=today, interview_date=today + timedelta(days=1)),
    ]
    async with SessionLocal() as session:
        await session.execute(applications.insert(), rows)
        await session.commit()
    yield


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
