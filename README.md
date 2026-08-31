# MyShows API Tests

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC.svg)](https://docs.pytest.org/)
[![Allure Report](https://img.shields.io/badge/reports-Allure-orange.svg)](https://allurereport.org/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![CI](https://github.com/Stacy-Firsova-QA/myshows_api_tests/actions/workflows/ci.yml/badge.svg)](https://github.com/Stacy-Firsova-QA/myshows_api_tests/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Автотесты для REST API учебного pet-проекта **MyShows** — бэкенда для трекинга просмотренных сериалов (аналог по духу [myshows.me](https://myshows.me), но собственная реализация без связи с реальным сервисом). Проект написан как демонстрация подхода к тестированию API "снизу вверх": через слой HTTP-запросов и через прямую проверку состояния в базе данных.

Изначально проект велся в приватном GitLab в рамках курса по автоматизации тестирования, сейчас перенесён и дооформлен для портфолио.

## Что покрыто тестами

| Метод | Endpoint | Сценарий | Маркер |
|---|---|---|---|
| GET | `/api/v1/series` | Получение списка сериалов: 0 / 1 / 3 записи в БД, валидация тела ответа по JSON Schema | `smoke` |
| GET | `/api/v1/series` | Запрос с невалидным значением `status` — проверка кода ошибки и структуры сообщения | `regress` |
| GET | `/api/v1/series/{id}` | Получение сериала по id, полная сверка тела ответа через `DeepDiff` | `smoke` |
| PUT | `/api/v1/series/{id}` | Обновление каждого поля сериала по отдельности + проверка, что изменения реально попали в БД | `regress` |

## Архитектура тестов

- **`helpers/api_session.py`** — тонкая обёртка над `requests.Session`: все запросы идут через единый метод `_send`, который автоматически прикладывает к Allure-отчёту URL, заголовки и тело запроса/ответа.
- **`fixtures/api_fixtures.py`** и **`fixtures/db_fixtures.py`** — фикстуры уровня API (сессия) и уровня БД (подключение, наполнение и очистка таблицы `series`, в том числе из SQL-сидов в `data/`).
- **`schemas/`** — JSON Schema для валидации структуры ответов API (`jsonschema`).
- **`config/`** — конфигурация (base URL, параметры подключения к Postgres), значения берутся из переменных окружения.
- Тесты не оставляют после себя данных: каждая фикстура, создающая записи, гарантированно их удаляет в teardown.
- Маркеры `smoke` / `regress` (см. `pytest.ini`) позволяют гибко выбирать набор тестов для прогона.

## Стек технологий

- **Python 3.12**, **pytest 9**
- **requests** — HTTP-клиент
- **psycopg 3** — проверка состояния напрямую в PostgreSQL
- **jsonschema** — валидация контракта ответа
- **deepdiff** — точное сравнение сложных объектов в теле ответа
- **pytest-check** — soft-assertions для проверки нескольких условий за один тест
- **allure-pytest** — отчётность
- **python-dotenv** — конфигурация через `.env`
- **Docker / docker-compose** — запуск тестов в изолированном окружении

## Структура проекта

```
myshows_api_tests/
├── config/               # конфигурация: base URL, параметры подключения к БД
│   ├── api_config.py
│   └── db_config.py
├── data/                 # SQL-сиды для параметризованных тестов
│   ├── zero_series.sql
│   ├── one_series.sql
│   └── three_series.sql
├── fixtures/             # pytest-фикстуры уровня API и БД
│   ├── api_fixtures.py
│   └── db_fixtures.py
├── helpers/              # вспомогательные обёртки и утилиты
│   ├── api_session.py    # обёртка над requests.Session с логированием в Allure
│   └── file_helpers.py
├── schemas/              # JSON Schema для валидации ответов API
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

## Быстрый старт (локально)

```bash
git clone https://github.com/Stacy-Firsova-QA/myshows_api_tests.git
cd myshows_api_tests

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env             # заполнить своими значениями
```

Запуск всех тестов с отчётом Allure:

```bash
pytest -v --alluredir=allure-results
allure serve allure-results
```

Запуск только smoke-тестов:

```bash
pytest -v -m smoke
```

## Запуск в Docker

```bash
docker-compose up --build
```

`docker-compose.yml` поднимает три сервиса: базу данных `msr-db` (Postgres), тестируемый бэкенд `msr-backend` и контейнер с тестами `api-tests`, который стартует после того, как бэкенд прошёл healthcheck.

> **Важно.** Образ `msr-backend` тянется из приватного Docker Registry учебной платформы и недоступен за её пределами — это ожидаемо, так как проект писался в рамках курса. Публично доступны структура тестов, конфигурация окружения и сам подход к оркестрации через `docker-compose`. Если у вас есть доступ к собственному инстансу бэкенда с совместимым API, тесты запустятся из коробки — достаточно указать актуальные `API_HOST` и параметры БД в `.env`.

## CI

В GitHub Actions (`.github/workflows/ci.yml`) на каждый push и pull request в `main` автоматически:

1. Устанавливаются зависимости из `requirements.txt`;
2. Код проверяется линтером [ruff](https://docs.astral.sh/ruff/);
3. Выполняется `pytest --collect-only` — sanity-проверка, что все тесты, фикстуры и импорты корректны.

Полный прогон тестов с реальными запросами к API в CI сознательно не запускается — он требует доступа к приватному бэкенду (см. раздел выше). Такой подход честно отражает границы применимости CI для pet-проекта, завязанного на закрытую инфраструктуру.

## Об авторе

**Anastasia Firsova** — QA Automation Engineer.
GitHub: [Stacy-Firsova-QA](https://github.com/Stacy-Firsova-QA)

## Лицензия

Проект распространяется под лицензией [MIT](LICENSE).
