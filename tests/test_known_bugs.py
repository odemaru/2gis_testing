"""Найденные дефекты сервиса, оформленные исполняемым кодом.

Каждый тест здесь описывает поведение, которого требует документация, и
помечен xfail со ссылкой на пункт баг-репорта (docs/bug_report.pdf). Поэтому
прогон остаётся зелёным на текущем состоянии сервиса, но дефекты не теряются:

* xfail  значит, что дефект воспроизводится и поведение не изменилось;
* XPASS  значит, что дефект исправлен. Из-за strict=True прогон в этом
         случае падает, чтобы факт исправления нельзя было пропустить.
"""

import time
from datetime import datetime
from email.utils import parsedate_to_datetime
from http import HTTPStatus

import pytest

from api.constants import TITLE_MAX_LENGTH, TOKEN_TTL_MS, Errors
from tests.assertions import assert_created, assert_error, assert_status
from tests.factories import OMIT, favorite, random_title

#: Допустимое расхождение времени сервера и created_at, секунды.
CREATED_AT_TOLERANCE_SEC = 60


@pytest.mark.xfail(
    strict=True,
    reason="BUG-1: сервис принимает title длиной 1000 при документированном "
           "пределе 999 символов",
)
def test_title_of_1000_characters_is_rejected(favorites_api, token):
    """Название длиннее 999 символов должно отклоняться."""
    length = TITLE_MAX_LENGTH + 1
    payload = favorite(title=random_title(min_length=length, max_length=length))

    response = favorites_api.create(payload, token=token)

    assert_error(response, HTTPStatus.BAD_REQUEST, Errors.TITLE_TOO_LONG)


@pytest.mark.xfail(
    strict=True,
    reason="BUG-2: токен продолжает работать дольше заявленных 2000 мс "
           "(фактически около 2700 мс)",
)
def test_token_expires_after_documented_ttl(favorites_api, token):
    """Через 2000 мс токен должен быть недействителен."""
    time.sleep(TOKEN_TTL_MS / 1000 + 0.1)

    response = favorites_api.create(favorite(), token=token)

    assert_error(response, HTTPStatus.UNAUTHORIZED, Errors.TOKEN_INVALID)


@pytest.mark.xfail(
    strict=True,
    reason="BUG-3: сочетание lat=0 и lon=0 роняет сервис в 500 Internal Server Error",
)
def test_zero_coordinates_are_accepted(favorites_api, token):
    """Точка (0, 0) лежит внутри допустимых диапазонов и должна создаваться."""
    payload = favorite(lat=0.0, lon=0.0)

    response = favorites_api.create(payload, token=token)

    assert_created(response, payload)


@pytest.mark.xfail(
    strict=True,
    reason="BUG-4: опечатка в тексте ошибки, 'обзательным' вместо 'обязательным'",
)
def test_missing_title_error_message_is_spelled_correctly(favorites_api, token):
    """Текст ошибки для title должен совпадать по форме с lat и lon."""
    response = favorites_api.create(favorite(title=OMIT), token=token)

    assert_error(response, HTTPStatus.BAD_REQUEST, Errors.TITLE_REQUIRED)


@pytest.mark.xfail(
    strict=True,
    reason="BUG-5: цвет проверяется без учёта регистра и сохраняется как прислали",
)
@pytest.mark.parametrize("color", ["blue", "Blue", "bLuE"])
def test_color_in_wrong_case_is_rejected(favorites_api, token, color):
    """Значения вне списка BLUE, GREEN, RED, YELLOW должны отклоняться."""
    response = favorites_api.create(favorite(color=color), token=token)

    assert_error(response, HTTPStatus.BAD_REQUEST, Errors.COLOR_INVALID)


@pytest.mark.xfail(
    strict=True,
    reason="BUG-6: created_at обгоняет время сервера на час, но помечен смещением +00:00",
)
def test_created_at_matches_server_time(favorites_api, token):
    """created_at должен соответствовать времени сервера из заголовка Date."""
    response = favorites_api.create(favorite(), token=token)
    assert_status(response, HTTPStatus.OK)

    server_time = parsedate_to_datetime(response.headers["Date"])
    created_at = datetime.fromisoformat(response.json()["created_at"])

    difference = abs((created_at - server_time).total_seconds())
    assert difference <= CREATED_AT_TOLERANCE_SEC, (
        f"created_at={created_at.isoformat()} расходится с временем сервера "
        f"{server_time.isoformat()} на {difference:.0f} с"
    )
