"""Тест-кейс #3: получение сессионного токена и авторизация запросов."""

from http import HTTPStatus

from api.constants import TOKEN_TTL_MS, Errors
from tests.assertions import assert_error, assert_status
from tests.factories import favorite


def test_token_is_issued(auth_api):
    """Сервис выдаёт токен в cookie с временем жизни из документации."""
    response = auth_api.create_token()

    assert_status(response, HTTPStatus.OK)
    assert response.cookies.get("token"), "Cookie 'token' отсутствует в ответе"
    assert f"Max-Age={TOKEN_TTL_MS // 1000}" in response.headers.get("Set-Cookie", ""), (
        f"Ожидался Max-Age={TOKEN_TTL_MS // 1000}, "
        f"получено: {response.headers.get('Set-Cookie')!r}"
    )


def test_request_without_token_is_rejected(favorites_api):
    """Запрос без cookie с токеном отклоняется."""
    response = favorites_api.create(favorite(), token=None)

    assert_error(response, HTTPStatus.UNAUTHORIZED, Errors.TOKEN_REQUIRED)


def test_request_with_unknown_token_is_rejected(favorites_api):
    """Несуществующий токен отклоняется."""
    response = favorites_api.create(favorite(), token="00000000000000000000000000000000")

    assert_error(response, HTTPStatus.UNAUTHORIZED, Errors.TOKEN_INVALID)


def test_token_is_reusable_within_ttl(favorites_api, token):
    """Один токен обслуживает несколько запросов, пока не истёк."""
    first = favorites_api.create(favorite(), token=token)
    second = favorites_api.create(favorite(), token=token)

    assert_status(first, HTTPStatus.OK)
    assert_status(second, HTTPStatus.OK)
