import pytest
import allure

from http import HTTPStatus
from config.api_config import API_HOST
from helpers.file_helpers import load_yaml
from jsonschema import validate
from deepdiff import DeepDiff

@allure.suite("Тесты GET на эндпоинт /series")
class TestGetSeries:

    @allure.title("Получение всех сериалов: позитивный сценарий")
    @pytest.mark.smoke
    @pytest.mark.parametrize("db_from_file", [
        "zero_series.sql",
        "one_series.sql",
        "three_series.sql"
    ],
        indirect=True
    )
    def test__series__without_params(self, api_session, db_from_file):
        with allure.step("Получаем список сериалов"):
            response = api_session.get(
                API_HOST + "/api/v1/series"
            )
        with allure.step("Проверяем код ответа"):
            assert response.status_code == HTTPStatus.OK
        with allure.step("Проверяем тело ответа"):
            body = response.json()
            assert len(body) == db_from_file
            template = load_yaml("series_get.yml")
            validate(body, template)

    @allure.title("Получение сериалов по невалидному статусу: негативный сценарий")
    @pytest.mark.regress
    def test__series__with_invalid_status(self, api_session, check):
        with allure.step("Получаем список сериалов"):
            response = api_session.get(
                API_HOST + "/api/v1/series",
                params={"status": "watch"}
            )
        with allure.step("Проверяем код ответа"):
            assert response.status_code == HTTPStatus.BAD_REQUEST
        with allure.step("Проверяем тело ответа"):
            body = response.json()
            with check:
                assert body["error"] == "validation error"
            with check:
                assert body["detail"] == [{'type': 'enum', 'loc': ['query', 'status'], 'msg': "Input should be 'watching', 'watched' or 'will_watch'", 'input': 'watch', 'ctx': {'expected': "'watching', 'watched' or 'will_watch'"}}]

    @allure.title("Получение сериалов по id: позитивный сценарий")
    @pytest.mark.smoke
    def test__series__by_id(self, api_session, db_insert_and_delete_series):
        with allure.step("Получаем сериал по заданному id"):
            response = api_session.get(
                API_HOST + "/api/v1/series/1",
            )
        with allure.step("Проверяем код ответа"):
            assert response.status_code == HTTPStatus.OK
        with allure.step("Проверяем тело ответа"):
            body = response.json()
            template_deep = {'id': 1,
                             'name': 'Breaking Bad',
                             'photo': 'https://avatars.mds.yandex.net/get-kinopoisk-image/1900788/fb35416f-3b0d-4b96-bc65-cf6923f9e329/600x900',
                             'rating': 9,
                             'review': 'Great series',
                             'status': 'watched'}
            compare = DeepDiff(
                template_deep, body,
                ignore_order=True
            )
            assert not compare, compare

@allure.suite("Тесты PUT на эндпоинт /series")
class TestPutSeries:

    @allure.title("Обновление сериала: позитивный сценарий")
    @pytest.mark.regress
    @pytest.mark.parametrize("field_name, new_value", [
        ("name", "Breaking Dad"),
        ("photo", "https://avatars.mds.yandex.net/get-ott/223007/2a0000016ffbfaa9040ccd53e970ea7e086a/600x900"),
        ("rating", 8),
        ("status", "watching"),
        ("review", "changed")
    ],
    # чтобы в консоли удобно было определять прогоны
    ids=["change name", "change photo", "change rating", "change status", "change review"]
    )
    def test__series__update_info(self, api_session, db_connection, db_insert_and_delete_one_series, field_name, new_value):
        base_json = {"name": "Breaking Bad",
                     "photo": "https://avatars.mds.yandex.net/get-kinopoisk-image/1900788/fb35416f-3b0d-4b96-bc65-cf6923f9e329/600x900",
                     "rating": 9, "status": "watched", "review": "Great series"}

        base_json[field_name] = new_value

        with allure.step("Обновляем информацию по сериалу"):
            response = api_session.put(
                API_HOST + f"/api/v1/series/{db_insert_and_delete_one_series}",
                json=base_json
            )

        body = response.json()

        with allure.step("Проверяем код ответа"):
            assert response.status_code == HTTPStatus.OK, body
        with allure.step("Проверяем обновление по сериалу в БД"):
            field_indexes = {
                "name": 0,
                "photo": 1,
                "rating": 2,
                "status": 3,
                "review": 4
            }
            with db_connection.transaction():
                with db_connection.cursor() as cur:
                    cur.execute("""
                        SELECT name, photo, rating, status, review
                        FROM series
                        WHERE id = %s
                    """, (db_insert_and_delete_one_series,))
                    result = cur.fetchone()
                    compare_with = field_indexes[field_name]
                    assert result[compare_with] == new_value
