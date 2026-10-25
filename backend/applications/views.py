from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, viewsets

from .models import Application
from .serializers import ApplicationSerializer, RegisterSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Create a new user account."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class ApplicationViewSet(viewsets.ModelViewSet):
    """CRUD for job applications. Users only ever see their own rows."""

    serializer_class = ApplicationSerializer
    filterset_fields = ("status", "company")
    search_fields = ("company", "role", "location")
    ordering_fields = ("applied_date", "created_at", "company", "interview_date")

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
