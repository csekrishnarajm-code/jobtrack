from django.conf import settings
from django.db import models


class Application(models.Model):
    class Status(models.TextChoices):
        WISHLIST = "wishlist", "Wishlist"
        APPLIED = "applied", "Applied"
        INTERVIEW = "interview", "Interview"
        OFFER = "offer", "Offer"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    company = models.CharField(max_length=120)
    role = models.CharField(max_length=120)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.APPLIED
    )
    location = models.CharField(max_length=120, blank=True)
    job_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    applied_date = models.DateField(null=True, blank=True)
    interview_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Explicit table name: the FastAPI analytics service reads this table.
        db_table = "job_applications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "applied_date"]),
        ]

    def __str__(self):
        return f"{self.role} @ {self.company} ({self.status})"
