from datetime import date, timedelta


def headers(token, user_id=1, **kw):
    return {"Authorization": f"Bearer {token(user_id, **kw)}"}


async def test_health(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


async def test_requires_token(client):
    assert (await client.get("/analytics/summary")).status_code in (401, 403)


async def test_rejects_bad_tokens(client, token):
    res = await client.get("/analytics/summary", headers={"Authorization": "Bearer garbage"})
    assert res.status_code == 401
    res = await client.get("/analytics/summary", headers=headers(token, secret="x" * 40))
    assert res.status_code == 401
    res = await client.get("/analytics/summary", headers=headers(token, token_type="refresh"))
    assert res.status_code == 401


async def test_summary_counts_and_rates(client, token):
    res = await client.get("/analytics/summary", headers=headers(token))
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 5  # user 2's row is excluded
    assert data["by_status"] == {
        "wishlist": 1, "applied": 1, "interview": 1, "offer": 1, "rejected": 1,
    }
    # submitted = 5 - 1 wishlist = 4 ; interview+offer = 2 -> 50% ; offer = 1 -> 25%
    assert data["interview_rate"] == 50.0
    assert data["offer_rate"] == 25.0


async def test_summary_empty_user(client, token):
    res = await client.get("/analytics/summary", headers=headers(token, user_id=99))
    data = res.json()
    assert data["total"] == 0
    assert data["interview_rate"] == 0.0


async def test_weekly_is_zero_filled_and_scoped(client, token):
    res = await client.get("/analytics/weekly?weeks=4", headers=headers(token))
    assert res.status_code == 200
    points = res.json()
    assert len(points) == 4
    assert sum(p["count"] for p in points) == 4  # 4 dated applications for user 1
    assert points[-1]["week_start"] == str(date.today() - timedelta(days=date.today().weekday()))


async def test_upcoming_interviews(client, token):
    res = await client.get("/analytics/upcoming-interviews", headers=headers(token))
    assert res.status_code == 200
    items = res.json()
    assert [i["company"] for i in items] == ["Freshworks"]  # past + other-user excluded


async def test_root_redirects_to_docs(client):
    res = await client.get("/", follow_redirects=False)
    assert res.status_code in (302, 307)
    assert res.headers["location"] == "/docs"
