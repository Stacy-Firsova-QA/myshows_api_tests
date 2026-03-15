import json
from textwrap import indent

from requests import Session
import allure

# Делаем свою оболочку для отправки запросов. _send -> главное звено, через которое проходят все запросы (общий центр).

class ApiSession:
    def __init__(self, session: Session):
        self.session = session

    def _send(self, method: str, url: str, **kwargs):
        response = self.session.request(method=method, url=url, **kwargs)
        request_body = response.request.body

        allure.attach(
            body=f"Request:\n"
                 f"URL: {response.request.url}\n"
                 f"Headers: {json.dumps(dict(response.request.headers), indent=4, ensure_ascii=False)}\n"
                 f"Body: {request_body}\n"
                 f"Response:\n"
                 f"Status code: {response.status_code}\n"
                 f"Headers: {json.dumps(dict(response.headers), indent=4, ensure_ascii=False)}\n"
                 f"Body: {json.dumps(response.json(), indent=4, ensure_ascii=False)}\n",
            name="Детальная информация о запросе и ответе",
            attachment_type=allure.attachment_type.TEXT,
        )
        return response

    @allure.step("GET-запрос к адресу {url}")
    def get(self, url: str, params: dict | None = None):
        return self._send("GET", url, params=params)

    @allure.step("PUT-запрос к адресу {url}")
    def put(self, url: str, json: dict | None = None, params: dict | None = None):
        return self._send("PUT", url, params=params, json=json)

