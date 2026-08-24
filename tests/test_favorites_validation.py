"""Тест-кейс #2: обработка некорректных параметров."""

from http import HTTPStatus

import pytest

from api.constants import (
    LAT_MAX,
    LAT_MIN,
    LON_MAX,
    LON_MIN,
    TITLE_MAX_LENGTH,
    Errors,
)
from tests.assertions import assert_error, assert_status
from tests.factories import OMIT, favorite, random_title

STEP = 0.000001


def test_empty_title_is_rejected(favorites_api, token):
    response = favorites_api.create(favorite(title=""), token=token)

    assert_error(response, HTTPStatus.BAD_REQUEST, Errors.TITLE_EMPTY)


@pytest.mark.parametrize(
    "length",
    [TITLE_MAX_LENGTH + 2, 5000],
    ids=["1001-chars", "5000-chars"],
)
def test_too_long_title_is_rejected(favorites_api, token, length):
    """Название длиннее допустимого отклоняется.

    Граничная длина 1000 сюда не входит: сервис её принимает вопреки
    документации, это оформлено как BUG-1 в tests/test_known_bugs.py.
    """
    payload = favorite(title=random_title(min_length=length, max_length=length))

    response = favorites_api.create(payload, token=token)

    assert_error(response, HTTPStatus.BAD_REQUEST, Errors.TITLE_TOO_LONG)


@pytest.mark.parametrize(
    "parameter, expected_message",
    [
        ("lat", Errors.LAT_REQUIRED),
        ("lon", Errors.LON_REQUIRED),
    ],
    ids=["lat", "lon"],
)
def test_missing_required_parameter_is_rejected(
    favorites_api, token, parameter, expected_message
):
    payload = favorite(**{parameter: OMIT})

    response = favorites_api.create(payload, token=token)

    assert_error(response, HTTPStatus.BAD_REQUEST, expected_message)


def test_missing_title_is_rejected(favorites_api, token):
    """Отсутствие обязательного title отклоняется.

    Проверяется только статус: текст сообщения сервис возвращает с опечаткой,
    сверка текста вынесена в BUG-4 в tests/test_known_bugs.py.
    """
    response = favorites_api.create(favorite(title=OMIT), token=token)

    assert_status(response, HTTPStatus.BAD_REQUEST)


@pytest.mark.parametrize(
    "lat, expected_message",
    [
        (LAT_MIN - STEP, Errors.LAT_TOO_SMALL),
        (LAT_MAX + STEP, Errors.LAT_TOO_BIG),
    ],
    ids=["below-min", "above-max"],
)
def test_latitude_out_of_range_is_rejected(favorites_api, token, lat, expected_message):
    response = favorites_api.create(favorite(lat=lat), token=token)

    assert_error(response, HTTPStatus.BAD_REQUEST, expected_message)


@pytest.mark.parametrize(
    "lon, expected_message",
    [
        (LON_MIN - STEP, Errors.LON_TOO_SMALL),
        (LON_MAX + STEP, Errors.LON_TOO_BIG),
    ],
    ids=["below-min", "above-max"],
)
def test_longitude_out_of_range_is_rejected(favorites_api, token, lon, expected_message):
    response = favorites_api.create(favorite(lon=lon), token=token)

    assert_error(response, HTTPStatus.BAD_REQUEST, expected_message)


@pytest.mark.parametrize(
    "parameter, value, expected_message",
    [
        ("lat", "abc", Errors.LAT_NOT_A_NUMBER),
        ("lon", "abc", Errors.LON_NOT_A_NUMBER),
        ("lat", "55,028254", Errors.LAT_NOT_A_NUMBER),
    ],
    ids=["lat-as-text", "lon-as-text", "comma-separator"],
)
def test_non_numeric_coordinate_is_rejected(
    favorites_api, token, parameter, value, expected_message
):
    payload = favorite(**{parameter: value})

    response = favorites_api.create(payload, token=token)

    assert_error(response, HTTPStatus.BAD_REQUEST, expected_message)


@pytest.mark.parametrize(
    "color",
    ["test", "BLUEGREEN", ""],
    ids=["arbitrary-string", "two-colors-joined", "empty-string"],
)
def test_invalid_color_is_rejected(favorites_api, token, color):
    response = favorites_api.create(favorite(color=color), token=token)

    assert_error(response, HTTPStatus.BAD_REQUEST, Errors.COLOR_INVALID)


def test_parameters_are_validated_in_order(favorites_api, token):
    """При нескольких ошибках сразу сервис сообщает о первом параметре.

    Порядок проверки: title -> lat -> lon -> color.
    """
    payload = favorite(title="", lat=LAT_MAX + 1, lon=LON_MAX + 1, color="test")

    response = favorites_api.create(payload, token=token)

    assert_error(response, HTTPStatus.BAD_REQUEST, Errors.TITLE_EMPTY)
