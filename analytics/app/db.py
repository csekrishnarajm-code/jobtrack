from sqlalchemy import Column, Date, Integer, MetaData, String, Table
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

metadata = MetaData()

# Read-only mapping of the table created and migrated by Django.
applications = Table(
    "job_applications",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, nullable=False),
    Column("company", String(120)),
    Column("role", String(120)),
    Column("status", String(20)),
    Column("applied_date", Date, nullable=True),
    Column("interview_date", Date, nullable=True),
)


async def get_session():
    async with SessionLocal() as session:
        yield session


__all__ = ["engine", "SessionLocal", "metadata", "applications", "get_session", "AsyncSession"]
