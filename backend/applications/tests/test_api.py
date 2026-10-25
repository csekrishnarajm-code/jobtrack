import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


def register_and_login(client, username="alice", password="StrongPass123!"):
    res = client.post(
        "/api/auth/register/",
        {"username": username, "email": f"{username}@example.com", "password": password},
        format="json",
    )
    assert res.status_code == 201, res.content
    res = client.post(
        "/api/auth/login/", {"username": username, "password": password}, format="json"
    )
    assert res.status_code == 200
    return res.data["access"]


def auth(client, token):
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


def payload(**overrides):
    data = {"company": "Acme", "role": "Python Developer", "status": "applied"}
    data.update(overrides)
    return data


def test_register_hashes_password(client):
    register_and_login(client)
    user = User.objects.get(username="alice")
    assert user.password != "StrongPass123!"
    assert user.check_password("StrongPass123!")


def test_register_rejects_weak_password(client):
    res = client.post(
        "/api/auth/register/",
        {"username": "bob", "email": "b@example.com", "password": "12345678"},
        format="json",
    )
    assert res.status_code == 400


def test_register_rejects_duplicate_email(client):
    register_and_login(client, "alice")
    res = client.post(
        "/api/auth/register/",
        {"username": "other", "email": "alice@example.com", "password": "StrongPass123!"},
        format="json",
    )
    assert res.status_code == 400


def test_login_wrong_password(client):
    register_and_login(client)
    res = client.post(
        "/api/auth/login/", {"username": "alice", "password": "nope"}, format="json"
    )
    assert res.status_code == 401


def test_endpoints_require_authentication(client):
    assert client.get("/api/applications/").status_code == 401
    assert client.post("/api/applications/", payload(), format="json").status_code == 401


def test_create_list_update_delete(client):
    auth(client, register_and_login(client))

    res = client.post("/api/applications/", payload(applied_date="2026-09-01"), format="json")
    assert res.status_code == 201
    app_id = res.data["id"]

    res = client.get("/api/applications/")
    assert res.status_code == 200
    assert res.data["count"] == 1

    res = client.patch(f"/api/applications/{app_id}/", {"status": "interview"}, format="json")
    assert res.status_code == 200
    assert res.data["status"] == "interview"

    assert client.delete(f"/api/applications/{app_id}/").status_code == 204
    assert client.get("/api/applications/").data["count"] == 0


def test_users_cannot_see_each_others_data(client):
    token_a = register_and_login(client, "alice")
    token_b = register_and_login(client, "bob")

    auth(client, token_a)
    app_id = client.post("/api/applications/", payload(), format="json").data["id"]

    auth(client, token_b)
    assert client.get("/api/applications/").data["count"] == 0
    assert client.get(f"/api/applications/{app_id}/").status_code == 404
    assert client.delete(f"/api/applications/{app_id}/").status_code == 404


def test_filter_search_and_ordering(client):
    auth(client, register_and_login(client))
    client.post("/api/applications/", payload(company="Zoho", status="applied"), format="json")
    client.post("/api/applications/", payload(company="Freshworks", status="interview"), format="json")
    client.post("/api/applications/", payload(company="Infosys", status="rejected"), format="json")

    res = client.get("/api/applications/?status=interview")
    assert [a["company"] for a in res.data["results"]] == ["Freshworks"]

    res = client.get("/api/applications/?search=zoh")
    assert [a["company"] for a in res.data["results"]] == ["Zoho"]

    res = client.get("/api/applications/?ordering=company")
    assert [a["company"] for a in res.data["results"]] == ["Freshworks", "Infosys", "Zoho"]


def test_invalid_status_and_dates_rejected(client):
    auth(client, register_and_login(client))
    assert client.post("/api/applications/", payload(status="banana"), format="json").status_code == 400
    res = client.post(
        "/api/applications/",
        payload(applied_date="2026-09-10", interview_date="2026-09-01"),
        format="json",
    )
    assert res.status_code == 400
    assert "interview_date" in res.data
