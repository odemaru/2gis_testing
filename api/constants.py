"""Константы сервиса: адрес, ограничения из документации и тексты ошибок."""

from typing import Final

DEFAULT_BASE_URL: Final[str] = "https://regions-test.2gis.com/v1"

# --- Ограничения, заявленные в документации к заданию ---------------------
TITLE_MIN_LENGTH: Final[int] = 1
TITLE_MAX_LENGTH: Final[int] = 999

LAT_MIN: Final[float] = -90.0
LAT_MAX: Final[float] = 90.0
LON_MIN: Final[float] = -180.0
LON_MAX: Final[float] = 180.0

COLORS: Final[tuple[str, ...]] = ("BLUE", "GREEN", "RED", "YELLOW")

#: Время жизни сессионного токена по документации, миллисекунды.
TOKEN_TTL_MS: Final[int] = 2000

#: Фактически измеренное время жизни токена, секунды (см. BUG-2 в баг-репорте).
#: Нужно, чтобы отличить проявление дефекта от медленной сети: если запрос
#: доехал до сервиса позже этого срока, токен истёк по-настоящему и проверка
#: ничего не доказывает.
MEASURED_TOKEN_TTL_SEC: Final[float] = 2.7


class Errors:
    """Тексты ошибок сервиса.

    Значения сняты с работающего API. Там, где фактический текст расходится
    с ожидаемым, здесь хранится ОЖИДАЕМЫЙ вариант, а расхождение оформлено
    отдельным тестом в tests/test_known_bugs.py.
    """

    # title
    TITLE_REQUIRED = "Параметр 'title' является обязательным"
    TITLE_EMPTY = "Параметр 'title' не может быть пустым"
    TITLE_TOO_LONG = "Параметр 'title' должен содержать не более 999 символов"

    # lat
    LAT_REQUIRED = "Параметр 'lat' является обязательным"
    LAT_TOO_SMALL = "Параметр 'lat' должен быть не менее -90"
    LAT_TOO_BIG = "Параметр 'lat' должен быть не более 90"
    LAT_NOT_A_NUMBER = "Параметр 'lat' должен быть числом"

    # lon
    LON_REQUIRED = "Параметр 'lon' является обязательным"
    LON_TOO_SMALL = "Параметр 'lon' должен быть не менее -180"
    LON_TOO_BIG = "Параметр 'lon' должен быть не более 180"
    LON_NOT_A_NUMBER = "Параметр 'lon' должен быть числом"

    # color
    COLOR_INVALID = (
        "Параметр 'color' может быть одним из следующих значений: "
        "BLUE, GREEN, RED, YELLOW"
    )

    # авторизация
    TOKEN_REQUIRED = "Параметр 'token' является обязательным"
    TOKEN_INVALID = "Передан несуществующий или «протухший» 'token'"
