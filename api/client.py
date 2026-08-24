"""Клиенты ручек тестируемого сервиса.

Клиент отвечает только за формирование запроса и возвращает сырой Response.
Проверки ответа (статус, схема, текст ошибки) остаются в тестах. Поэтому
тест падает на строке с assert, а не внутри транспортного слоя.
"""

from requests import Response

from api.http import Http


class AuthApi:
    """Ручка выдачи сессионного токена: POST /auth/tokens."""

    PATH = "/auth/tokens"

    def __init__(self, base_url: str, http: Http):
        self._base_url = base_url
        self._http = http

    def create_token(self) -> Response:
        """Запросить новый токен. Тело запроса пустое, токен придёт в cookie."""
        return self._http.request("POST", f"{self._base_url}{self.PATH}")


class FavoritesApi:
    """Ручка создания избранного места: POST /favorites."""

    PATH = "/favorites"

    def __init__(self, base_url: str, http: Http):
        self._base_url = base_url
        self._http = http

    def create(self, payload: dict, token: str | None = None) -> Response:
        """Создать избранное место.

        :param payload: параметры формы (title, lat, lon, color)
        :param token: сессионный токен. None означает запрос без cookie,
                      это отдельный проверяемый сценарий авторизации
        """
        cookies = {"token": token} if token is not None else None
        return self._http.request(
            "POST",
            f"{self._base_url}{self.PATH}",
            data=payload,
            cookies=cookies,
        )
