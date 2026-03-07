import pytest
from http import HTTPStatus
from config.api_config import HOST
from helpers.file_helpers import load_yaml
from jsonschema import validate
from deepdiff import DeepDiff


class TestGetSeries:
    @pytest.mark.smoke
    def test__series__without_params(self, api_session, db_insert_and_delete_series):
        response = api_session.get(
            HOST + "/api/v1/series"
        )
        assert response.status_code == HTTPStatus.OK
        body = response.json()
        template = load_yaml("series_get.yml")
        validate(body, template)

    @pytest.mark.regress
    def test__series__with_invalid_status(self, api_session, check):
        response = api_session.get(
            HOST + "/api/v1/series",
            params={"status": "watch"}
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        body = response.json()
        with check:
            assert body["error"] == "validation error"
        with check:
            assert body["detail"] == [{'type': 'enum', 'loc': ['query', 'status'], 'msg': "Input should be 'watching', 'watched' or 'will_watch'", 'input': 'watch', 'ctx': {'expected': "'watching', 'watched' or 'will_watch'"}}]

    @pytest.mark.smoke
    def test__series__by_id(self, api_session, db_insert_and_delete_series):
        response = api_session.get(
            HOST + "/api/v1/series/1",
        )
        assert response.status_code == HTTPStatus.OK
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




