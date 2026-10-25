from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Application

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        read_only_fields = ("id",)

    def validate_email(self, value):
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        # Run Django's password validators (length, common passwords, ...).
        temp_user = User(username=attrs.get("username"), email=attrs.get("email", ""))
        validate_password(attrs["password"], user=temp_user)
        return attrs

    def create(self, validated_data):
        # create_user hashes the password; it is never stored in plain text.
        return User.objects.create_user(**validated_data)


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = (
            "id",
            "company",
            "role",
            "status",
            "location",
            "job_url",
            "notes",
            "applied_date",
            "interview_date",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        applied = attrs.get("applied_date", getattr(self.instance, "applied_date", None))
        interview = attrs.get(
            "interview_date", getattr(self.instance, "interview_date", None)
        )
        if applied and interview and interview < applied:
            raise serializers.ValidationError(
                {"interview_date": "Interview date cannot be before the applied date."}
            )
        return attrs
