from pathlib import Path

import allure
import psycopg
import pytest

from config.db_config import DB_CONN_PARAMS


@pytest.fixture(scope="session")
def db_connection():
    with allure.step("Создание подключения к БД"):
        conn = psycopg.connect(**DB_CONN_PARAMS)
    yield conn
    with allure.step("Закрытие подключения к БД"):
        conn.close()


@pytest.fixture()
def db_insert_and_delete_series(db_connection):
    series_data = [
        ("Breaking Bad", "https://avatars.mds.yandex.net/get-kinopoisk-image/1900788/fb35416f-3b0d-4b96-bc65-cf6923f9e329/600x900", 9, "watched", "Great series"),
        ("Game of Thrones", "https://avatars.mds.yandex.net/get-ott/223007/2a0000016ffbfaa9040ccd53e970ea7e086a/600x900", 9, "will_watch", "Epic fantasy"),
        ("Friends", "https://avatars.mds.yandex.net/get-kinopoisk-image/4486454/bae692d9-8260-46a4-9188-8509a72aa005/600x900", 8, "watching", "Classic sitcom"),
        ("Sherlock", "https://avatars.mds.yandex.net/get-kinopoisk-image/1629390/f28c1ea2-47b0-49d5-b11c-9608744f0233/600x900", 8, "watched", "Detective story"),
    ]

    created_ids = []

    with allure.step("Наполнение таблицы сериалами"):
        try:
            with db_connection.transaction(), db_connection.cursor() as cur:
                for s in series_data:
                    cur.execute("""
                            INSERT INTO series(name, photo, rating, status, review)
                            VALUES(%s, %s, %s, %s, %s)
                            RETURNING id
                        """, s)
                    created_ids.append(cur.fetchone()[0])
        except psycopg.Error as e:
            print(f"Ошибка при сохранении данных в БД: {e}")
            raise

    yield created_ids

    with allure.step("Полное очищение таблицы"):
        try:
            with db_connection.transaction(), db_connection.cursor() as cur:
                cur.execute("""
                        TRUNCATE TABLE series RESTART IDENTITY
                    """)
        except psycopg.Error as e:
            print(f"Ошибка при удалении данных в БД: {e}")
            raise

@pytest.fixture()
def db_insert_and_delete_one_series(db_connection):
    series_data = ("Breaking Bad", "https://avatars.mds.yandex.net/get-kinopoisk-image/1900788/fb35416f-3b0d-4b96-bc65-cf6923f9e329/600x900", 9, "watched", "Great series")
    created_id = None

    with allure.step("Создание одной записи сериала"):
        try:
            with db_connection.transaction(), db_connection.cursor() as cur:
                cur.execute("""
                        INSERT INTO series(name, photo, rating, status, review)
                        VALUES(%s, %s, %s, %s, %s)
                        RETURNING id
                    """, series_data)
                created_id = cur.fetchone()[0]
        except psycopg.Error as e:
            print(f"Ошибка при сохранении данных в БД: {e}")
            raise

    yield created_id

    with allure.step("Точечное удаление записи сериала"):
        try:
            with db_connection.transaction(), db_connection.cursor() as cur:
                cur.execute("""
                        DELETE FROM series WHERE id = %s
                    """, (created_id,))
        except psycopg.Error as e:
            print(f"Ошибка при удалении данных в БД: {e}")
            raise

@pytest.fixture()
def db_from_file(db_connection, request):
    if hasattr(request, "param"):
        filename = request.param
    else:
        filename = "three_series.sql"

    with allure.step("Чтение SQL-скрипта из файла"):
        path = Path(__file__).parent.parent / "data" / filename
        sql_script = path.read_text(encoding="utf-8")

    result = 0

    with allure.step("Создание записей сериалов(-а) из файла и подсчет созданных записей(-и)"):
        try:
            with db_connection.transaction(), db_connection.cursor() as cur:
                cur.execute(sql_script)
                cur.execute("""
                        SELECT COUNT(*)
                        FROM series
                    """)
                result = cur.fetchone()[0]
        except psycopg.Error as e:
            print(f"Ошибка при работе с БД: {e}")
            raise

    yield result

    with allure.step("Полное удаление созданных записей(-и)"):
        try:
            with db_connection.transaction(), db_connection.cursor() as cur:
                cur.execute("""
                        TRUNCATE TABLE series RESTART IDENTITY
                    """)
        except psycopg.Error as e:
            print(f"Ошибка при удалении данных в БД: {e}")
            raise


