# MyShows API Tests

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC.svg)](https://docs.pytest.org/)
[![Allure Report](https://img.shields.io/badge/reports-Allure-orange.svg)](https://allurereport.org/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![CI](https://github.com/Stacy-Firsova-QA/myshows_api_tests/actions/workflows/ci.yml/badge.svg)](https://github.com/Stacy-Firsova-QA/myshows_api_tests/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

API test suite for **MyShows** — a pet-project backend for tracking watched TV series. The project demonstrates a "bottom-up" approach to API testing: verifying behavior both through the HTTP layer and by checking state directly in the database.

## What's covered

| Method | Endpoint | Scenario | Marker |
|---|---|---|---|
| GET | `/api/v1/series` | Get the list of series: 0 / 1 / 3 records in the DB, response body validated against a JSON Schema | `smoke` |
| GET | `/api/v1/series` | Request with an invalid `status` value — checks the error code and error message structure | `regress` |
| GET | `/api/v1/series/{id}` | Get a series by id, full response body comparison via `DeepDiff` | `smoke` |
| PUT | `/api/v1/series/{id}` | Update each field of a series individually + verify the change was actually persisted in the DB | `regress` |

## Test architecture

- **`helpers/api_session.py`** — a thin wrapper around `requests.Session`: every request goes through a single `_send` method, which automatically attaches the request/response URL, headers and body to the Allure report.
- **`fixtures/api_fixtures.py`** and **`fixtures/db_fixtures.py`** — API-level (session) and DB-level fixtures (connection, seeding and cleaning up the `series` table, including from SQL seed files in `data/`).
- **`schemas/`** — JSON Schema files used to validate the structure of API responses (`jsonschema`).
- **`config/`** — configuration (base URL, Postgres connection parameters), values are read from environment variables.
- Tests leave no data behind: every fixture that creates records is guaranteed to remove them again in teardown.
- `smoke` / `regress` markers (see `pytest.ini`) allow flexible selection of which tests to run.

## Tech stack

- **Python 3.12**, **pytest 9**
- **requests** — HTTP client
- **psycopg 3** — verifying state directly in PostgreSQL
- **jsonschema** — response contract validation
- **deepdiff** — precise comparison of complex objects in the response body
- **pytest-check** — soft assertions for checking multiple conditions in a single test
- **allure-pytest** — reporting
- **python-dotenv** — configuration via `.env`
- **Docker / docker-compose** — running tests in an isolated environment

## Project structure

```
myshows_api_tests/
├── config/               # configuration: base URL, DB connection parameters
│   ├── api_config.py
│   └── db_config.py
├── data/                 # SQL seed files for parametrized tests
│   ├── zero_series.sql
│   ├── one_series.sql
│   └── three_series.sql
├── fixtures/              # pytest fixtures for the API and DB layers
│   ├── api_fixtures.py
│   └── db_fixtures.py
├── helpers/               # helper wrappers and utilities
│   ├── api_session.py    # wrapper over requests.Session with Allure logging
│   └── file_helpers.py
├── schemas/               # JSON Schema files for validating API responses
│   └── series_get.yml
├── tests/
│   └── test_myshows_api.py
├── conftest.py
├── pytest.ini
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Quick start (local)

```bash
git clone https://github.com/Stacy-Firsova-QA/myshows_api_tests.git
cd myshows_api_tests

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env             # fill in your own values
```

Run all tests with an Allure report:

```bash
pytest -v --alluredir=allure-results
allure serve allure-results
```

Run only smoke tests:

```bash
pytest -v -m smoke
```

## Running in Docker

```bash
docker-compose up --build
```

`docker-compose.yml` spins up three services: the database `msr-db` (Postgres), the backend under test `msr-backend`, and the test runner `api-tests`, which starts once the backend passes its healthcheck.

> **Note.** The `msr-backend` image is pulled from a private Docker Registry and isn't publicly accessible — the backend was originally built as part of a testing course. What's fully public here is the test suite, the environment configuration, and the `docker-compose` orchestration approach itself. If you have access to your own instance of a compatible backend, the tests will run out of the box — just point `API_HOST` and the DB parameters in `.env` to it.

## CI

On every push and pull request to `main`, GitHub Actions (`.github/workflows/ci.yml`) automatically:

1. Installs dependencies from `requirements.txt`;
2. Lints the code with [ruff](https://docs.astral.sh/ruff/);
3. Runs `pytest --collect-only` as a sanity check that all tests, fixtures and imports are valid.

The full test run against a live API is intentionally not executed in CI, since it requires access to the private backend (see the note above). This keeps CI honest about what it actually verifies for a pet-project tied to closed infrastructure.

## Author

**Anastasia Firsova** — QA Automation Engineer.
GitHub: [Stacy-Firsova-QA](https://github.com/Stacy-Firsova-QA)

## License

This project is licensed under the [MIT License](LICENSE).
