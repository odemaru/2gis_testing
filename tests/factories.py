"""Фабрика тестовых данных для метода создания избранного места."""

import random
import string
from typing import Any, Final

from api.constants import (
    LAT_MAX,
    LAT_MIN,
    LON_MAX,
    LON_MIN,
    TITLE_MAX_LENGTH,
    TITLE_MIN_LENGTH,
)


class _Omit:
    """Маркер «параметр не передавать»."""

    def __repr__(self) -> str:
        return "OMIT"


#: Явный маркер отсутствия параметра в запросе.
#:
#: Нужен, чтобы отличать два разных сценария, которые легко перепутать:
#:   favorite(lat=OMIT) значит, что параметра lat в форме нет вообще
#:   favorite(lat="")   значит, что параметр есть, но пустой
#: Передать для этого None нельзя: requests молча выбрасывает None-поля из
#: формы, и тест «пустое значение» незаметно превращается в тест «нет поля».
OMIT: Final = _Omit()

CYRILLIC: Final[str] = (
    "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
)
#: Алфавит из документации: латиница, кириллица, цифры и знаки препинания.
TITLE_ALPHABET: Final[str] = (
    CYRILLIC + string.ascii_letters + string.digits + string.punctuation
)


def random_title(
    min_length: int = TITLE_MIN_LENGTH,
    max_length: int = TITLE_MAX_LENGTH,
) -> str:
    """Название места допустимой длины из допустимых символов."""
    length = random.randint(min_length, max_length)
    return "".join(random.choice(TITLE_ALPHABET) for _ in range(length))


def random_lat() -> float:
    return round(random.uniform(LAT_MIN, LAT_MAX), 6)


def random_lon() -> float:
    return round(random.uniform(LON_MIN, LON_MAX), 6)


def favorite(**overrides: Any) -> dict[str, Any]:
    """Валидный набор параметров с точечной подменой полей.

    Намерение теста читается прямо в месте вызова::

        favorite()                     # валидное место со случайными данными
        favorite(title="")             # пустое название
        favorite(lat=LAT_MAX + 0.000001)  # широта вне диапазона
        favorite(lat=OMIT)             # обязательный параметр не передан
        favorite(color="BLUE")         # с явным цветом

    Необязательный параметр color по умолчанию не передаётся. В этом случае
    сервис должен вернуть null.
    """
    payload: dict[str, Any] = {
        "title": random_title(),
        "lat": random_lat(),
        "lon": random_lon(),
    }
    payload.update(overrides)
    return {key: value for key, value in payload.items() if value is not OMIT}
