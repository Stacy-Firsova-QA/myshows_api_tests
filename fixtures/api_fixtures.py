import requests
import pytest
import allure
from requests import Session
from helpers.api_session import ApiSession


@pytest.fixture(scope="session")
def api_session():
    with allure.step("Создание API сессии"):
        with requests.Session() as myshows_session:
            # чтобы requests не читал системные прокси-настройки и не использовал их, а шел напрямую на хост
            myshows_session.trust_env = False
            # теперь возвращаем не голую сессию, а обертку над ней (см. helpers/api_session.py)
            yield ApiSession(myshows_session)

