"""Фикстуры и настройки запуска."""

from http import HTTPStatus
from typing import Callable

import pytest

from api.client import AuthApi, FavoritesApi
from api.constants import DEFAULT_BASE_URL
from api.http import Http


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--base-url",
        action="store",
        default=DEFAULT_BASE_URL,
        help=f"Базовый адрес тестируемого сервиса (по умолчанию {DEFAULT_BASE_URL})",
    )


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--base-url")


@pytest.fixture(scope="session")
def http() -> Http:
    return Http()


@pytest.fixture(scope="session")
def auth_api(base_url: str, http: Http) -> AuthApi:
    return AuthApi(base_url, http)


@pytest.fixture(scope="session")
def favorites_api(base_url: str, http: Http) -> FavoritesApi:
    return FavoritesApi(base_url, http)


@pytest.fixture
def new_token(auth_api: AuthApi) -> Callable[[], str]:
    """Фабрика токенов: выдаёт новый токен на каждый вызов.

    Нужна там, где тест делает несколько запросов подряд и одного токена
    может не хватить из-за его короткого времени жизни.
    """

    def create() -> str:
        response = auth_api.create_token()
        assert response.status_code == HTTPStatus.OK, (
            f"Не удалось получить токен: {response.status_code} {response.text[:200]}"
        )
        value = response.cookies.get("token")
        assert value, "В ответе на запрос токена отсутствует cookie 'token'"
        return value

    return create


@pytest.fixture
def token(new_token: Callable[[], str]) -> str:
    """Свежий сессионный токен на каждый тест.

    Скоуп именно function, а не session: токен живёт около двух секунд,
    и общий на всю сессию токен протух бы уже на втором тесте, уронив
    весь прогон в 401.
    """
    return new_token()
