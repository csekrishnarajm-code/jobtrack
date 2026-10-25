# Sample Output

Real output captured from a live run of this project (Django on port 8000, FastAPI on port 8001,
sharing one database and one JWT secret). Dates are relative to the day it was run.

Reproduce it yourself after `docker compose up`:

```bash
python scripts/demo.py
```

## 1. Live API demo (`scripts/demo.py`)

```text
=== 1. Register user  (HTTP 201) ===
{
  "id": 1,
  "username": "demo",
  "email": "demo@example.com"
}

=== 2. Login  (HTTP 200) ===
Got access token: eyJhbGciOiJIUzI1NiIsInR5c...

=== 3. Create Zoho / Python Developer  (HTTP 201) ===

=== 3. Create Freshworks / Backend Developer  (HTTP 201) ===

=== 3. Create Infosys / Python Developer  (HTTP 201) ===

=== 3. Create TCS / Software Engineer  (HTTP 201) ===

=== 3. Create Google / Software Engineer  (HTTP 201) ===

=== 4. Django: filter applications by status=interview  (HTTP 200) ===
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "company": "Zoho",
      "role": "Python Developer",
      "status": "interview",
      "location": "",
      "job_url": "",
      "notes": "",
      "applied_date": "2026-10-20",
      "interview_date": "2026-10-30",
      "created_at": "2026-10-24T07:26:57.557240Z",
      "updated_at": "2026-10-24T07:26:57.557260Z"
    }
  ]
}

=== 5. Django: search 'python', ordered by company  (HTTP 200) ===
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 3,
      "company": "Infosys",
      "role": "Python Developer",
      "status": "offer",
      "location": "",
      "job_url": "",
      "notes": "",
      "applied_date": "2026-10-12",
      "interview_date": null,
      "created_at": "2026-10-24T07:26:57.570485Z",
      "updated_at": "2026-10-24T07:26:57.570511Z"
    },
    {
      "id": 1,
      "company": "Zoho",
      "role": "Python Developer",
      "status": "interview",
      "location": "",
      "job_url": "",
      "notes": "",
      "applied_date": "2026-10-20",
      "interview_date": "2026-10-30",
      "created_at": "2026-10-24T07:26:57.557240Z",
      "updated_at": "2026-10-24T07:26:57.557260Z"
    }
  ]
}

=== 6. FastAPI: /analytics/summary  (HTTP 200) ===
{
  "total": 5,
  "by_status": {
    "wishlist": 1,
    "applied": 1,
    "interview": 1,
    "offer": 1,
    "rejected": 1
  },
  "interview_rate": 50.0,
  "offer_rate": 25.0
}

=== 7. FastAPI: /analytics/weekly?weeks=4  (HTTP 200) ===
[
  {
    "week_start": "2026-09-28",
    "count": 0
  },
  {
    "week_start": "2026-10-05",
    "count": 1
  },
  {
    "week_start": "2026-10-12",
    "count": 1
  },
  {
    "week_start": "2026-10-19",
    "count": 2
  }
]

=== 8. FastAPI: /analytics/upcoming-interviews  (HTTP 200) ===
[
  {
    "id": 1,
    "company": "Zoho",
    "role": "Python Developer",
    "interview_date": "2026-10-30"
  }
]

=== 9. FastAPI without a token  (HTTP 401) - correctly rejected ===

Demo finished. Everything above came from a live run of the project.
```

## 2. Django test suite (`cd backend && pytest -v`)

```text
applications/tests/test_api.py::test_register_hashes_password PASSED
applications/tests/test_api.py::test_register_rejects_weak_password PASSED
applications/tests/test_api.py::test_register_rejects_duplicate_email PASSED
applications/tests/test_api.py::test_login_wrong_password PASSED
applications/tests/test_api.py::test_endpoints_require_authentication PASSED
applications/tests/test_api.py::test_create_list_update_delete PASSED
applications/tests/test_api.py::test_users_cannot_see_each_others_data PASSED
applications/tests/test_api.py::test_filter_search_and_ordering PASSED
applications/tests/test_api.py::test_invalid_status_and_dates_rejected PASSED
applications/tests/test_dburl.py::test_parses_neon_style_url PASSED
applications/tests/test_dburl.py::test_url_without_ssl_and_custom_port PASSED
applications/tests/test_dburl.py::test_rejects_other_schemes PASSED
applications/tests/test_dburl.py::test_root_redirects_to_docs PASSED
============================= 13 passed in 17.79s ==============================
```

## 3. FastAPI test suite (`cd analytics && pytest -v`)

```text
tests/test_analytics.py::test_health PASSED
tests/test_analytics.py::test_requires_token PASSED
tests/test_analytics.py::test_rejects_bad_tokens PASSED
tests/test_analytics.py::test_summary_counts_and_rates PASSED
tests/test_analytics.py::test_summary_empty_user PASSED
tests/test_analytics.py::test_weekly_is_zero_filled_and_scoped PASSED
tests/test_analytics.py::test_upcoming_interviews PASSED
tests/test_analytics.py::test_root_redirects_to_docs PASSED
tests/test_config.py::test_converts_neon_url_for_asyncpg PASSED
tests/test_config.py::test_plain_postgres_url_without_ssl PASSED
tests/test_config.py::test_async_urls_unchanged PASSED
============================== 11 passed in 0.17s ==============================
```

## What this proves

- A user can register and log in; passwords are hashed and validated.
- Applications support create, list, filter, search, ordering and pagination.
- The FastAPI service accepts the **same JWT** issued by Django and returns analytics only for that user.
- Requests without a valid token are rejected with HTTP 401.
