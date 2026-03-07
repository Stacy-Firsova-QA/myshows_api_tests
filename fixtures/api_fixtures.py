import requests
import pytest
from requests import Session


@pytest.fixture(scope="session")
def api_session():
    with requests.Session() as myshows_session:
        # чтобы requests не читал системные прокси-настройки и не использовал их, а шел напрямую на хост
        myshows_session.trust_env = False
        yield myshows_session

