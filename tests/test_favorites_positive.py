"""Тест-кейс #1: создание избранного места с корректными параметрами."""

from http import HTTPStatus

import pytest

from api.constants import (
    COLORS,
    LAT_MAX,
    LAT_MIN,
    LON_MAX,
    LON_MIN,
    TITLE_MAX_LENGTH,
    TITLE_MIN_LENGTH,
)
from tests.assertions import assert_created, assert_status
from tests.factories import favorite, random_title


def test_create_favorite_with_random_data(favorites_api, token):
    """Место создаётся, ответ соответствует схеме и повторяет отправленные данные."""
    payload = favorite()

    response = favorites_api.create(payload, token=token)

    assert_created(response, payload)


def test_color_is_null_when_not_sent(favorites_api, token):
    """Необязательный color по умолчанию возвращается как null."""
    payload = favorite()

    response = favorites_api.create(payload, token=token)

    body = assert_created(response, payload)
    assert body["color"] is None, f"Ожидался null, получено {body['color']!r}"


@pytest.mark.parametrize("color", COLORS)
def test_create_favorite_with_each_valid_color(favorites_api, token, color):
    """Все документированные цвета принимаются и возвращаются без изменений."""
    payload = favorite(color=color)

    response = favorites_api.create(payload, token=token)

    assert_created(response, payload)


@pytest.mark.parametrize(
    "length",
    [TITLE_MIN_LENGTH, TITLE_MAX_LENGTH],
    ids=["min-length-1", "max-length-999"],
)
def test_create_favorite_with_boundary_title_length(favorites_api, token, length):
    """Границы допустимой длины названия принимаются."""
    payload = favorite(title=random_title(min_length=length, max_length=length))

    response = favorites_api.create(payload, token=token)

    body = assert_created(response, payload)
    assert len(body["title"]) == length


@pytest.mark.parametrize(
    "lat, lon",
    [
        (LAT_MIN, LON_MIN),
        (LAT_MIN, LON_MAX),
        (LAT_MAX, LON_MIN),
        (LAT_MAX, LON_MAX),
        (0.0, 82.918501),
        (55.028254, 0.0),
    ],
    ids=[
        "lat-min/lon-min", "lat-min/lon-max", "lat-max/lon-min", "lat-max/lon-max",
        "zero-lat", "zero-lon",
    ],
)
def test_create_favorite_with_boundary_coordinates(favorites_api, token, lat, lon):
    """Границы диапазонов координат входят в допустимые значения.

    Сочетание (0, 0) сюда намеренно не включено: на нём сервис отвечает 500,
    это оформлено отдельно как BUG-3 в tests/test_known_bugs.py.
    """
    payload = favorite(lat=lat, lon=lon)

    response = favorites_api.create(payload, token=token)

    assert_created(response, payload)


def test_id_increases_monotonically(favorites_api, token):
    """Идентификатор нового места монотонно возрастает."""
    ids = []
    for _ in range(3):
        response = favorites_api.create(favorite(), token=token)
        assert_status(response, HTTPStatus.OK)
        ids.append(response.json()["id"])

    assert ids == sorted(set(ids)), f"Идентификаторы не возрастают монотонно: {ids}"
