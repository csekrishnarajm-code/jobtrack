from datetime import date

from pydantic import BaseModel


class Summary(BaseModel):
    total: int
    by_status: dict[str, int]
    interview_rate: float  # % of submitted applications that reached interview/offer
    offer_rate: float  # % of submitted applications that became offers


class WeeklyPoint(BaseModel):
    week_start: date
    count: int


class UpcomingInterview(BaseModel):
    id: int
    company: str
    role: str
    interview_date: date
