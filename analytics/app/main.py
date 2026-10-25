from datetime import date, timedelta

from fastapi import Depends, FastAPI
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import get_current_user_id
from .config import STATUSES
from .db import applications, get_session
from .schemas import Summary, UpcomingInterview, WeeklyPoint

app = FastAPI(
    title="JobTrack Analytics API",
    description="Async analytics service for the JobTrack Django backend. "
    "Authenticate with the JWT access token from the Django login endpoint.",
    version="1.0.0",
)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs")


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok"}


@app.get("/analytics/summary", response_model=Summary, tags=["analytics"])
async def summary(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """Totals per status plus interview and offer rates."""
    result = await session.execute(
        select(applications.c.status, func.count())
        .where(applications.c.user_id == user_id)
        .group_by(applications.c.status)
    )
    by_status = {s: 0 for s in STATUSES}
    for status_name, count in result.all():
        by_status[status_name] = count

    total = sum(by_status.values())
    submitted = total - by_status["wishlist"]  # wishlist = not applied yet
    interviews = by_status["interview"] + by_status["offer"]
    interview_rate = round(interviews / submitted * 100, 1) if submitted else 0.0
    offer_rate = round(by_status["offer"] / submitted * 100, 1) if submitted else 0.0

    return Summary(
        total=total,
        by_status=by_status,
        interview_rate=interview_rate,
        offer_rate=offer_rate,
    )


@app.get("/analytics/weekly", response_model=list[WeeklyPoint], tags=["analytics"])
async def weekly(
    weeks: int = 8,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """Applications submitted per week for the last N weeks (default 8)."""
    weeks = max(1, min(weeks, 52))
    this_monday = date.today() - timedelta(days=date.today().weekday())
    first_monday = this_monday - timedelta(weeks=weeks - 1)

    result = await session.execute(
        select(applications.c.applied_date).where(
            applications.c.user_id == user_id,
            applications.c.applied_date.is_not(None),
            applications.c.applied_date >= first_monday,
        )
    )
    buckets = {first_monday + timedelta(weeks=i): 0 for i in range(weeks)}
    for (applied,) in result.all():
        monday = applied - timedelta(days=applied.weekday())
        if monday in buckets:
            buckets[monday] += 1

    return [WeeklyPoint(week_start=w, count=c) for w, c in buckets.items()]


@app.get(
    "/analytics/upcoming-interviews",
    response_model=list[UpcomingInterview],
    tags=["analytics"],
)
async def upcoming_interviews(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """Next 10 interviews from today onwards."""
    result = await session.execute(
        select(
            applications.c.id,
            applications.c.company,
            applications.c.role,
            applications.c.interview_date,
        )
        .where(
            applications.c.user_id == user_id,
            applications.c.interview_date.is_not(None),
            applications.c.interview_date >= date.today(),
        )
        .order_by(applications.c.interview_date)
        .limit(10)
    )
    return [
        UpcomingInterview(id=r.id, company=r.company, role=r.role, interview_date=r.interview_date)
        for r in result.all()
    ]
