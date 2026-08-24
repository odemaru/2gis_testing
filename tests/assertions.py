"""Общие шаги проверки ответа.

Вынесены из тестов, чтобы каждый тест читался как два шага задания:
сформировать запрос и сравнить результат с ожидаемым.
"""

from http import HTTPStatus
from typing import Any

from requests import Response

from api.schemas import ERROR_SCHEMA, FAVORITE_SCHEMA, validate_schema


def _json(response: Response) -> Any:
    """Разобрать тело как JSON с понятным сообщением, если это не JSON."""
    try:
        return response.json()
    except ValueError:
        raise AssertionError(
            f"Ожидался JSON, получено "
            f"Content-Type={response.headers.get('Content-Type')!r}, "
            f"тело={response.text[:200]!r}"
        ) from None


def assert_status(response: Response, expected: HTTPStatus) -> None:
    assert response.status_code == expected, (
        f"Ожидался статус {expected} {expected.phrase}, "
        f"получен {response.status_code}. Тело: {response.text[:300]}"
    )


def assert_created(response: Response, expected_payload: dict) -> dict:
    """Проверить успешное создание: статус, схема и эхо отправленных данных."""
    assert_status(response, HTTPStatus.OK)

    body = _json(response)
    validate_schema(body, FAVORITE_SCHEMA)

    assert body["title"] == expected_payload["title"], "Название не совпало"
    assert float(body["lat"]) == float(expected_payload["lat"]), "Широта не совпала"
    assert float(body["lon"]) == float(expected_payload["lon"]), "Долгота не совпала"
    assert body["color"] == expected_payload.get("color"), "Цвет не совпал"
    return body


def assert_error(
    response: Response,
    expected_status: HTTPStatus,
    expected_message: str,
) -> None:
    """Проверить ответ с ошибкой: статус, схема конверта и текст сообщения."""
    assert_status(response, expected_status)

    body = _json(response)
    validate_schema(body, ERROR_SCHEMA)

    actual_message = body["error"]["message"]
    assert actual_message == expected_message, (
        f"Ожидалось сообщение {expected_message!r}, получено {actual_message!r}"
    )
