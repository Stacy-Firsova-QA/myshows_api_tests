import psycopg
import pytest

from config.db_config import DB_CONN_PARAMS


@pytest.fixture(scope="session")
def db_connection():
    conn = psycopg.connect(**DB_CONN_PARAMS)
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def db_insert_and_delete_series(db_connection):
    series_data = [
        ("Breaking Bad", "https://avatars.mds.yandex.net/get-kinopoisk-image/1900788/fb35416f-3b0d-4b96-bc65-cf6923f9e329/600x900", 9, "watched", "Great series"),
        ("Game of Thrones", "https://avatars.mds.yandex.net/get-ott/223007/2a0000016ffbfaa9040ccd53e970ea7e086a/600x900", 9, "will_watch", "Epic fantasy"),
        ("Friends", "https://avatars.mds.yandex.net/get-kinopoisk-image/4486454/bae692d9-8260-46a4-9188-8509a72aa005/600x900", 8, "watching", "Classic sitcom"),
        ("Sherlock", "https://avatars.mds.yandex.net/get-kinopoisk-image/1629390/f28c1ea2-47b0-49d5-b11c-9608744f0233/600x900", 8, "watched", "Detective story"),
    ]

    created_ids = []

    try:
        with db_connection.transaction():
            with db_connection.cursor() as cur:
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

    try:
        with db_connection.transaction():
            with db_connection.cursor() as cur:
                cur.execute("""
                    TRUNCATE TABLE series RESTART IDENTITY
                """)
    except psycopg.Error as e:
        print(f"Ошибка при удалении данных в БД: {e}")
        raise
